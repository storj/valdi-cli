import os
import stat
import tarfile
import tempfile
from pathlib import Path

import requests

from valdi.config.settings import Config


class Initializer:
    @staticmethod
    def initialize():
        if Config.BACKEND == Config.Goofys:
            Initializer._initialize_goofys()
        elif Config.BACKEND == Config.CunoFS:
            Initializer._initialize_cunofs()

    @staticmethod
    def _initialize_goofys():
        present_working_dir = Path(__file__)
        top_level_dir = present_working_dir.parent.parent.parent
        file_to_check = top_level_dir / Config.Goofys.EXE_FILE
        if not file_to_check.exists():
            response = requests.get(Config.Goofys.URL)
            response.raise_for_status()
            with open(file_to_check, "wb") as f:
                f.write(response.content)

        current_permissions = file_to_check.stat().st_mode
        if not os.access(file_to_check, os.X_OK):
            new_permissions = current_permissions | stat.S_IXUSR
            os.chmod(file_to_check, new_permissions)

        goofys_credentials_filepath = Path(Config.Goofys.CREDENTIALS_FILE).expanduser()
        os.makedirs(goofys_credentials_filepath.parent, exist_ok=True)
        with open(goofys_credentials_filepath, "a", encoding="utf8"):
            os.utime(goofys_credentials_filepath, None)

    @staticmethod
    def _initialize_cunofs():
        present_working_dir = Path(__file__)
        top_level_dir = present_working_dir.parent.parent.parent
        if (top_level_dir / Config.CunoFS.BASE_FOLDER).is_dir():
            return
        with tempfile.TemporaryDirectory(dir=top_level_dir) as td:
            response = requests.get(Config.CunoFS.URL, stream=True)
            response.raise_for_status()
            with tarfile.open(mode="r|*", fileobj=response.raw) as tf:
                tf.extractall(td)
            os.rename(Path(td) / "cuno", Path(td) / "dist")
            os.mkdir(Path(td) / "volumes")
            os.rename(Path(td), top_level_dir / Config.CunoFS.BASE_FOLDER)
