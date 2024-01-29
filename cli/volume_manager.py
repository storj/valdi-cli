import os
import subprocess
from pathlib import Path
from config.settings import Config
from cli.authenticator import Authenticator


class VolumeManager:
    def __init__(self, authenticator: Authenticator):
        self.authenticator = authenticator

    @staticmethod
    def _volume_access_credentials_are_available(volume_name):
        if Config.GOOFYS_CREDENTIALS_FILE.exists():
            with open(Config.GOOFYS_CREDENTIALS_FILE, 'r') as f:
                for line in f:
                    if line.strip() == f'[{volume_name}]':
                        return True
            return False
        else:
            raise RuntimeError('Volume credentials file is missing, this CLI tool has likely not been initialized.')

    @staticmethod
    def _store_volume_access_credentials(volume_name):
        access_key = input('Enter access key: ')
        secret_key = input('Enter secret access key: ')
        with open(Config.GOOFYS_CREDENTIALS_FILE, 'a') as f:
            f.write(f'[{volume_name}]\naws_access_key_id = {access_key}\naws_secret_access_key = {secret_key}\n')

    def mount_volume(self, prefix_to_mount, mountpoint):
        present_working_dir = Path(__file__)
        goofys_exe = present_working_dir.parent.parent / Config.GOOFYS_EXE_FILE
        mount_point = Path(mountpoint)
        if not mount_point.is_absolute():
            raise RuntimeError('mountpoint must be a full path')
        os.makedirs(mount_point, exist_ok=True)

        if not self._volume_access_credentials_are_available(prefix_to_mount):
            self._store_volume_access_credentials(prefix_to_mount)

        original_aws_profile = os.environ.get('AWS_PROFILE')
        os.environ['AWS_PROFILE'] = prefix_to_mount
        try:
            subprocess.run([
                goofys_exe,
                '--endpoint',
                Config.VALDI_GATEWAY_URL,
                f'{Config.VALDI_GLOBAL_ROOT}:{self.authenticator.user_info["user_id"]}/{prefix_to_mount}',
                mountpoint
            ],
                check=True
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f'Error mounting volume: {e.stderr}')
        finally:
            if original_aws_profile is not None:
                os.environ['AWS_PROFILE'] = original_aws_profile
            else:
                os.environ.pop('AWS_PROFILE', None)

    @staticmethod
    def unmount_volume(mountpoint):
        if not Path(mountpoint).is_absolute():
            raise RuntimeError('mountpoint must be a full path')
        try:
            subprocess.run([
                'umount',
                mountpoint
            ],
                check=True
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f'Error unmounting volume: {e.stderr}')
