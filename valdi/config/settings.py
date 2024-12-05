class Config:
    GATEWAY_URL = "https://gateway.valdi.ai"
    CREDENTIALS_FILE = ".valdi/credentials"
    BASE_URL = "https://api.valdi.ai"
    GLOBAL_ROOT = "valdi"

    class Goofys:
        URL = "https://github.com/kahing/goofys/releases/latest/download/goofys"
        CREDENTIALS_FILE = "~/.aws/credentials"
        EXE_FILE = "goofys"

    class CunoFS:
        URL = (
            "https://link.storjshare.io/raw/<redacted>/"
            "cuno-dist/cuno-dist-v1.2.6.tar.gz"
        )
        BASE_FOLDER = "cunofs"
        VER_FILE = "1.2.5"

    BACKEND = Goofys
