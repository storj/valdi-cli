#!/usr/bin/env python3

"""
volume_manager manages delegation of mounting object storage prefixes into
the filesystem.
"""

__copyright__ = "Copyright (C) 2024 Storj Labs, Inc."

import getpass
import json
import os
import subprocess
import tempfile
import time
from pathlib import Path

from valdi.cli import TerminalError
from valdi.cli.authenticator import Authenticator
from valdi.config.settings import Config


def _request_credentials():
    access_key = input("Enter access key: ")
    secret_key = getpass.getpass("Enter secret access key: ")
    return access_key, secret_key


class GoofysVolumeManager:
    def __init__(self, authenticator: Authenticator):
        self.authenticator = authenticator

    @staticmethod
    def _volume_access_credentials_are_available(volume_name):
        goofys_credentials_file = Path(Config.Goofys.CREDENTIALS_FILE).expanduser()
        if goofys_credentials_file.exists():
            with open(goofys_credentials_file, "r", encoding="utf8") as f:
                for line in f:
                    if line.strip() == f"[{volume_name}]":
                        return True
            return False
        raise TerminalError(
            'This CLI tool appears to be uninitialized. Run "valdi init" first.'
        )

    @staticmethod
    def _store_volume_access_credentials(volume_name):
        access_key, secret_key = _request_credentials()
        goofys_credentials_file = Path(Config.Goofys.CREDENTIALS_FILE).expanduser()
        with open(goofys_credentials_file, "a", encoding="utf8") as f:
            f.write(
                f"[{volume_name}]\n"
                f"aws_access_key_id = {access_key}\n"
                f"aws_secret_access_key = {secret_key}\n"
            )

    def mount_volume(self, volume_name, mountpoint):
        present_working_dir = Path(__file__)
        goofys_exe = present_working_dir.parent.parent.parent / Config.Goofys.EXE_FILE
        mount_point = Path(mountpoint).expanduser()
        if not mount_point.is_absolute():
            raise TerminalError("mountpoint must be a full path")
        os.makedirs(mount_point, exist_ok=True)

        if not self._volume_access_credentials_are_available(volume_name):
            self._store_volume_access_credentials(volume_name)

        subproc_environ = os.environ.copy()
        subproc_environ["AWS_PROFILE"] = volume_name
        try:
            subprocess.run(
                [
                    goofys_exe,
                    "--endpoint",
                    Config.GATEWAY_URL,
                    (
                        f"{Config.GLOBAL_ROOT}:"
                        f'{self.authenticator.user_info["user_id"]}/'
                        f"{volume_name}"
                    ),
                    mount_point,
                ],
                check=True,
                env=subproc_environ,
            )
        except subprocess.CalledProcessError as e:
            raise TerminalError(f"Error mounting volume: {e.stderr}") from e

    @staticmethod
    def unmount_volume(mountpoint):
        if not Path(mountpoint).is_absolute():
            raise TerminalError("mountpoint must be a full path")

        try:
            subprocess.run(["umount", mountpoint], check=True)
        except subprocess.CalledProcessError as e:
            raise TerminalError(
                f'Error unmounting volume{f": {e.stderr}" if e.stderr is not None else ""}'
            ) from e


class CunoFSVolumeManager:
    def __init__(self, authenticator: Authenticator):
        self.authenticator = authenticator

        present_working_dir = Path(__file__)
        top_level_dir = present_working_dir.parent.parent.parent
        self.path_to_cuno = top_level_dir / Config.CunoFS.BASE_FOLDER

    def _assert_volume_configured(self, volume_name):
        volume_path = self.path_to_cuno / "volumes" / volume_name
        if volume_path.exists():
            return
        access_key, secret_key = _request_credentials()
        with tempfile.TemporaryDirectory(dir=self.path_to_cuno) as td:
            os.makedirs(Path(td) / "creds" / "bindpoint" / "s3" / "bucketstore")
            os.makedirs(Path(td) / "creds" / "bindpoint" / "s3" / "credstore")
            os.makedirs(Path(td) / "cache")
            with open(Path(td) / "ver", "w", encoding="utf8") as fh:
                fh.write(Config.CunoFS.VER_FILE)
            with open(
                Path(td)
                / "creds"
                / "bindpoint"
                / "s3"
                / "bucketstore"
                / (Config.GLOBAL_ROOT + ".s3c"),
                "w",
                encoding="utf8",
            ) as fh:
                fh.write(
                    json.dumps(
                        {
                            "Credpath": ("s3/credstore/" + Config.GLOBAL_ROOT + ".s3c"),
                            "Region": "us-west-1",
                            "Timestamp": str(int(time.time())),
                            "Billing": "BucketOwner",
                            "SAS": "",
                        }
                    )
                )
            with open(
                Path(td)
                / "creds"
                / "bindpoint"
                / "s3"
                / "credstore"
                / (Config.GLOBAL_ROOT + ".s3c"),
                "w",
                encoding="utf8",
            ) as fh:
                fh.write(
                    f"aws_access_key_id = {access_key}\n"
                    f"aws_secret_access_key = {secret_key}\n"
                    f"endpoint = {Config.GATEWAY_URL}\n"
                    f"host = Storj\n"
                )
            os.rename(td, self.path_to_cuno / "volumes" / volume_name)

    def mount_volume(self, volume_name, mountpoint):
        self._assert_volume_configured(volume_name)

        subproc_env = os.environ.copy()
        subproc_env["CUNO_CREDENTIALS"] = (
            self.path_to_cuno / "volumes" / volume_name / "creds"
        )
        subproc_env["CUNO_OPTIONS"] = "+cachehome=" + str(
            self.path_to_cuno / "volumes" / volume_name / "cache"
        )
        subproc_env["CUNO_BASEDIR"] = self.path_to_cuno / "dist"
        subprocess.run(
            [
                str(self.path_to_cuno / "dist" / "bin" / "cuno"),
                "mount",
                mountpoint,
                "--root",
                (
                    f"s3://{Config.GLOBAL_ROOT}/"
                    f'{self.authenticator.user_info["user_id"]}/'
                    f"{volume_name}/"
                ),
                "--mkdir",
                "--no-allow-root",
            ],
            check=True,
            env=subproc_env,
        )

    @staticmethod
    def unmount_volume(mountpoint):
        subprocess.run(["umount", mountpoint], check=True)


def make_volume_manager(auth: Authenticator):
    if Config.BACKEND == Config.Goofys:
        return GoofysVolumeManager(auth)
    if Config.BACKEND == Config.CunoFS:
        return CunoFSVolumeManager(auth)
    raise RuntimeError("unknown backend in config")
