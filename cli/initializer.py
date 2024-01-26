import os
import stat
import requests
from pathlib import Path
from config.settings import Config


class Initializer:
    @staticmethod
    def initialize():
        present_working_dir = Path(__file__)
        top_level_dir = present_working_dir.parent
        file_to_check = top_level_dir / 'goofys'
        if not file_to_check.exists():
            response = requests.get(Config.GOOFYS_URL)
            response.raise_for_status()
            with open(file_to_check, 'wb') as f:
                f.write(response.content)
        else:
            current_permissions = file_to_check.stat().st_mode
            if not os.access(file_to_check, os.X_OK):
                new_permissions = current_permissions | stat.S_IXUSR
                os.chmod(file_to_check, new_permissions)