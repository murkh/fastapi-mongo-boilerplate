import os
from typing import List
from ..core.storage_provider import StorageService
from ..core.exceptions import NotFoundException
from ..core.config import settings


class LocalStorageService(StorageService):
    BASE_DIR = settings.LOCAL_STORAGE_PATH

    def list_directory(self, path: str):
        abs_path = os.path.abspath(os.path.join(self.BASE_DIR, path))
        base_dir_abs = os.path.abspath(self.BASE_DIR)
        if not abs_path.startswith(base_dir_abs):
            raise NotFoundException(
                detail="Access outside base directory is not allowed")
        if not os.path.exists(abs_path):
            raise NotFoundException(detail="Directory Not Found")

        return [{
            "name": entry,
            "is_dir": os.path.isdir(os.path.join(abs_path, entry)),
            "size": None if os.path.isdir(os.path.join(abs_path, entry)) else os.path.getsize(os.path.join(abs_path, entry))
        } for entry in os.listdir(abs_path)]

    def download_file(self, path: str) -> bytes:
        abs_path = os.path.abspath(os.path.join(self.BASE_DIR, path))
        base_dir_abs = os.path.abspath(self.BASE_DIR)
        if not abs_path.startswith(base_dir_abs):
            raise NotFoundException(
                detail="Access outside base directory is not allowed")
        if not os.path.exists(abs_path):
            raise NotFoundException(detail="File Not Found")
        with open(abs_path, "rb") as f:
            return f.read()
