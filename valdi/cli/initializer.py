import os
import stat
from pathlib import Path

import requests

from valdi.config.settings import Config


class Initializer:
    @staticmethod
    def initialize():
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
