import os
import sys
import getpass
import subprocess
from pathlib import Path

from valdi.config.settings import Config
from valdi.cli.authenticator import Authenticator


class VolumeManager:
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
        print('This CLI tool appears to be uninitialized. Run "valdi init" first.')
        sys.exit(1)

    @staticmethod
    def _store_volume_access_credentials(volume_name):
        access_key = input("Enter access key: ")
        secret_key = getpass.getpass("Enter secret access key: ")
        goofys_credentials_file = Path(Config.Goofys.CREDENTIALS_FILE).expanduser()
        with open(goofys_credentials_file, "a", encoding="utf8") as f:
            f.write(
                f"[{volume_name}]\n"
                f"aws_access_key_id = {access_key}\n"
                f"aws_secret_access_key = {secret_key}\n"
            )

    def mount_volume(self, prefix_to_mount, mountpoint):
        present_working_dir = Path(__file__)
        goofys_exe = present_working_dir.parent.parent.parent / Config.Goofys.EXE_FILE
        mount_point = Path(mountpoint).expanduser()
        if not mount_point.is_absolute():
            print("mountpoint must be a full path")
            sys.exit(1)
        os.makedirs(mount_point, exist_ok=True)

        if not self._volume_access_credentials_are_available(prefix_to_mount):
            self._store_volume_access_credentials(prefix_to_mount)

        original_aws_profile = os.environ.get("AWS_PROFILE")
        os.environ["AWS_PROFILE"] = prefix_to_mount
        try:
            subprocess.run(
                [
                    goofys_exe,
                    "--endpoint",
                    Config.GATEWAY_URL,
                    (
                        f"{Config.GLOBAL_ROOT}:"
                        f'{self.authenticator.user_info["user_id"]}/'
                        f"{prefix_to_mount}"
                    ),
                    mount_point,
                ],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"Error mounting volume: {e.stderr}")
            sys.exit(1)
        finally:
            if original_aws_profile is not None:
                os.environ["AWS_PROFILE"] = original_aws_profile
            else:
                os.environ.pop("AWS_PROFILE", None)

    @staticmethod
    def unmount_volume(mountpoint):
        if not Path(mountpoint).is_absolute():
            print("mountpoint must be a full path")
            sys.exit(1)

        try:
            subprocess.run(["umount", mountpoint], check=True)
        except subprocess.CalledProcessError as e:
            print(
                f'Error unmounting volume{f": {e.stderr}" if e.stderr is not None else ""}'
            )
            sys.exit(1)
