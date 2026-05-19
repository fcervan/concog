import os
import boto3
from botocore.client import Config
from datetime import datetime

class StorageClient:
    def __init__(self):
        self.env = os.getenv("ENV", "local")
        self.bucket = "concog"
        self.base_path = "cc/arquivo-original"

        if self.env == "local":
            self.client = boto3.client(
                "s3",
                endpoint_url=os.getenv("MINIO_ENDPOINT", "http://localhost:9009"),
                aws_access_key_id=os.getenv("MINIO_ACCESS_KEY", "admin"),
                aws_secret_access_key=os.getenv("MINIO_SECRET_KEY", "password"),
                config=Config(signature_version="s3v4"),
                region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
            )
        else:
            self.client = boto3.client("s3")

    def _build_path(self, cliente_id: int, arquivo_parser_id: int, usuario_id: int, filename: str) -> str:
        now = datetime.now()
        return f"{self.base_path}/{now.year}/{now.month:02d}/{now.day:02d}/{cliente_id}/{arquivo_parser_id}/{usuario_id}/{filename}"

    def upload_file(self, file_content: bytes, cliente_id: int, arquivo_parser_id: int, usuario_id: int, filename: str) -> str:
        s3_path = self._build_path(cliente_id, arquivo_parser_id, usuario_id, filename)

        self.client.put_object(
            Bucket=self.bucket,
            Key=s3_path,
            Body=file_content,
            ContentType=self._get_content_type(filename)
        )

        return s3_path

    def _get_content_type(self, filename: str) -> str:
        ext = filename.lower().split(".")[-1]
        types = {
            "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "xls": "application/vnd.ms-excel",
            "csv": "text/csv"
        }
        return types.get(ext, "application/octet-stream")

storage = StorageClient()
