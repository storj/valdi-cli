#!/usr/bin/env python3

"""
entrypoint is used for running this package as a CLI tool.
"""

__copyright__ = "Copyright (C) 2024 Storj Labs, Inc."

import argparse
import sys

from valdi.cli import TerminalError
from valdi.cli.authenticator import Authenticator
from valdi.cli.initializer import Initializer
from valdi.cli.volume_manager import make_volume_manager


def init(args):
    Initializer.initialize()
    print("Successfully initialized")


def mount(args, volume_manager):
    volume_manager.mount_volume(args.volume_name, args.mountpoint)


def unmount(args, volume_manager):
    volume_manager.unmount_volume(args.mountpoint)


def main():
    parser = argparse.ArgumentParser(prog="valdi")
    subparsers = parser.add_subparsers(required=True, metavar="service")

    # init service
    init_parser = subparsers.add_parser("init", help="Initialize VALDI CLI")
    init_parser.set_defaults(service_func=init)

    # helper to create shared dependencies for volume subcommands
    def volume(args):
        auth = Authenticator()
        volume_manager = make_volume_manager(auth)
        args.command_func(args, volume_manager)

    # volume service
    volume_parser = subparsers.add_parser("volume", help="Manage detachable volumes")
    volume_parser.set_defaults(service_func=volume)
    volume_subparsers = volume_parser.add_subparsers(required=True, metavar="command")

    # volume mount command
    mount_parser = volume_subparsers.add_parser(
        "mount", help="Mount a detachable volume"
    )
    mount_parser.set_defaults(command_func=mount)
    mount_parser.add_argument("volume_name", help="Name of volume to mount")
    mount_parser.add_argument("mountpoint", help="Mount point for your volume")

    # volume unmount command
    unmount_parser = volume_subparsers.add_parser(
        "unmount", help="Unmount a detachable volume"
    )
    unmount_parser.set_defaults(command_func=unmount)
    unmount_parser.add_argument("mountpoint", help="Mount point of volume to unmount")

    # route commands
    args = parser.parse_args()
    try:
        args.service_func(args)
    except TerminalError as err:
        print(err)
        sys.exit(1)


if __name__ == "__main__":
    main()
