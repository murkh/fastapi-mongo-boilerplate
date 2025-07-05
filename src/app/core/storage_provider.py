from abc import ABC, abstractmethod
from typing import List


class StorageService(ABC):
    @abstractmethod
    def list_directory(self, path: str) -> List[dict]: pass

    @abstractmethod
    def download_file(self, path: str) -> bytes: pass
