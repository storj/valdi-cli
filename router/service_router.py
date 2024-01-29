from cli.volume_manager import VolumeManager
from cli.authenticator import Authenticator
from cli.initializer import Initializer
from config.settings import Config


class ServiceRouter:
    @staticmethod
    def route_to_service(service, cmd, *params):
        if service == Config.Service.INIT.value:
            # initialize CLI tool
            Initializer.initialize()
            print('Successfully initialized')
        else:
            auth = Authenticator()
            if service == Config.Service.VOLUME.value:
                # handle VOLUME commands
                volume_manager = VolumeManager(auth)
                if cmd == Config.Command.MOUNT.value:
                    print(f'Mount volume with params {params[0]}')
                elif cmd == Config.Command.UNMOUNT.value:
                    print('Unmount volume')
                else:
                    raise RuntimeError(f'Unrecognized command for {service} service')
            elif service == Config.Service.VM.value:
                # handle VM commands
                raise NotImplementedError('VM services not yet implemented')
            else:
                raise RuntimeError('Unrecognized service')
