from enum import Enum


class Config:
    GOOFYS_URL = 'https://github.com/kahing/goofys/releases/latest/download/goofys'
    VALDI_GATEWAY_URL = 'https://gateway.storjshare.io'
    VALDI_CREDENTIALS_FILE = '.valdi/credentials'
    GOOFYS_CREDENTIALS_FILE = '~/.aws/credentials'
    VALDI_BASE_URL = 'https://api.valdi.ai'
    VALDI_GLOBAL_ROOT = 'valdi'
    GOOFYS_EXE_FILE = 'goofys'

    class Service(Enum):
        VOLUME = 'volume'
        INIT = 'init'

    class VolumeCommand(Enum):
        MOUNT = 'mount'
        UNMOUNT = 'unmount'

    class VmCommand(Enum):
        START = 'start'
        STOP = 'stop'

    class Command(Enum):
        MOUNT = 'mount'
        UNMOUNT = 'unmount'
