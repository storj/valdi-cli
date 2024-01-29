import argparse
from config.settings import Config
from router.service_router import ServiceRouter


def main():
    parser = argparse.ArgumentParser()

    service_choices = [service.value for service in Config.Service]
    command_choices = [command.value for command in Config.Command]

    parser.add_argument('service', type=str, choices=service_choices)
    parser.add_argument('cmd', type=str, choices=command_choices)
    parser.add_argument('params', nargs='*', help='Additional parameters for this command')

    args = parser.parse_args()
    ServiceRouter.route_to_service(args.service, args.cmd, *args.params)


if __name__ == "__main__":
    main()
