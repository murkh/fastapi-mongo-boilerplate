from .local_storage import LocalStorageService


def get_local_storage_service() -> LocalStorageService:
    return LocalStorageService()
