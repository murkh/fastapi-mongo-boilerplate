import os
from typing import List
from ..core.storage_provider import StorageService
from ..core.exceptions import NotFoundException
from ..core.config import settings


class LocalStorageService(StorageService):
    def list_directory_tree(self, path: str, max_depth: int = 5):
        """Recursively list directory as a nested tree structure, up to max_depth."""
        abs_path = os.path.abspath(os.path.join(self.BASE_DIR, path))
        base_dir_abs = os.path.abspath(self.BASE_DIR)
        if not abs_path.startswith(base_dir_abs):
            raise NotFoundException(
                detail="Access outside base directory is not allowed")
        if not os.path.exists(abs_path):
            raise NotFoundException(detail="Directory Not Found")

        def build_tree(current_path, depth):
            if depth > max_depth:
                return []
            items = []
            for entry in os.listdir(current_path):
                entry_path = os.path.join(current_path, entry)
                if os.path.isdir(entry_path):
                    items.append({
                        "name": entry,
                        "is_dir": True,
                        "children": build_tree(entry_path, depth + 1)
                    })
                else:
                    items.append({
                        "name": entry,
                        "is_dir": False,
                        "size": os.path.getsize(entry_path)
                    })
            return items

        return build_tree(abs_path, 1)
    BASE_DIR = settings.LOCAL_STORAGE_PATH

    def list_directory(self, path: str):
        """List Directory for the given path"""
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
        """DOwnload the file from the given path"""
        abs_path = os.path.abspath(os.path.join(self.BASE_DIR, path))
        base_dir_abs = os.path.abspath(self.BASE_DIR)
        if not abs_path.startswith(base_dir_abs):
            raise NotFoundException(
                detail="Access outside base directory is not allowed")
        if not os.path.exists(abs_path):
            raise NotFoundException(detail="File Not Found")
        with open(abs_path, "rb") as f:
            return f.read()
