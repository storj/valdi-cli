from valdi.cli.volume_manager import VolumeManager
from valdi.cli.authenticator import Authenticator
from valdi.cli.initializer import Initializer
from valdi.config.settings import Config


class ServiceRouter:
    @staticmethod
    def route_to_service(args):
        if args.service == Config.Service.INIT.value:
            # initialize CLI tool
            Initializer.initialize()
            print('Successfully initialized')
        else:
            auth = Authenticator()
            if args.service == Config.Service.VOLUME.value:
                # handle VOLUME commands
                volume_manager = VolumeManager(auth)
                if args.cmd == Config.Command.MOUNT.value:
                    volume_manager.mount_volume(args.volume_name, args.mountpoint)
                elif args.cmd == Config.Command.UNMOUNT.value:
                    volume_manager.unmount_volume(args.mountpoint)
                else:
                    raise RuntimeError(f'Unrecognized command for {args.service} service')
            elif args.service == Config.Service.VM.value:
                # handle VM commands
                raise NotImplementedError('VM services not yet implemented')
            else:
                raise RuntimeError('Unrecognized service')
