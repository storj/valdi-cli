import argparse
from config.settings import Config
from router.service_router import ServiceRouter


def main():
    parser = argparse.ArgumentParser(prog='valdi')
    subparsers = parser.add_subparsers(dest='service', required=True, metavar='service')

    for service in Config.Service:
        if service.value == Config.Service.VOLUME.value:
            commands_enum = Config.VolumeCommand
            commands_list = ', '.join([command.value for command in commands_enum])
            service_parser = subparsers.add_parser(service.value, help=f'Possible commands: {commands_list}')

            service_subparsers = service_parser.add_subparsers(dest='cmd', required=True, metavar='command')
            for cmd in Config.VolumeCommand:
                if cmd.value == Config.VolumeCommand.MOUNT.value:
                    cmd_parser = service_subparsers.add_parser(
                        cmd.value,
                        help='Mount a detachable volume'
                    )
                    cmd_parser.add_argument('volume_name', help='Name of volume to mount')
                    cmd_parser.add_argument('mountpoint', help='Mount point on your VM')
                elif cmd.value == Config.VolumeCommand.UNMOUNT.value:
                    cmd_parser = service_subparsers.add_parser(
                        cmd.value,
                        help='Unmount a detachable volume'
                    )
                    cmd_parser.add_argument('mountpoint', help='Mount point of volume to unmount')
        elif service.value == 'vm':
            pass
        elif service.value == 'init':
            service_parser = subparsers.add_parser(service.value, help='Initialize VALDI CLI')

    args = parser.parse_args()
    # ServiceRouter.route_to_service(args.service, args.cmd, *args.params)
    print(args)


if __name__ == "__main__":
    main()
