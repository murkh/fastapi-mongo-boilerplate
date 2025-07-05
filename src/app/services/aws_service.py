from time import sleep
import boto3
from ..core.storage_provider import StorageService
from ..core.config import settings
from ..core.exceptions import NotFoundException, InternalServerException


class AWSStorageService(StorageService):
    def __init__(self, bucket_name: str):
        self.bucket = bucket_name
        self.client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )

    def list_directory(self, prefix: str):
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket, Prefix=prefix,)
            contents = response.get("Contents", [])
            return [{
                "name": obj["Key"],
                "is_dir": obj["Key"].endswith("/"),
                "size": obj.get("Size")
            } for obj in contents]
        except self.client.exceptions.NoSuchBucket:
            raise NotFoundException(f"Bucket '{self.bucket}' not found.")
        except self.client.exceptions.NoSuchKey:
            raise NotFoundException(
                f"File '{prefix}' not found in bucket '{self.bucket}'.")
        except Exception as e:
            raise InternalServerException(str(e))

    def download_file(self, path):
        try:
            obj = self.client.get_object(Bucket=self.bucket, Key=path)
            return obj["Body"].read()
        except self.client.exceptions.NoSuchKey:
            raise NotFoundException(
                f"File '{path}' not found in bucket '{self.bucket}'.")
        except self.client.exceptions.NoSuchBucket:
            raise NotFoundException(f"Bucket '{self.bucket}' not found.")
        except Exception as e:
            raise InternalServerException(str(e))
