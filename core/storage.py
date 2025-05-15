from minio import Minio
from minio.error import S3Error
from django.conf import settings
import urllib.parse
import logging

logger = logging.getLogger(__name__)

class MinioStorage:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_USE_SSL
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                # Set bucket policy to public
                policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {"AWS": "*"},
                            "Action": ["s3:GetObject"],
                            "Resource": [f"arn:aws:s3:::{self.bucket_name}/*"]
                        }
                    ]
                }
                self.client.set_bucket_policy(self.bucket_name, policy)
        except S3Error as e:
            logger.error(f"Error ensuring bucket exists: {e}")
            raise

    def get_presigned_put_url(self, object_name, expires=3600):
        try:
            url = self.client.presigned_put_object(
                self.bucket_name,
                object_name,
                expires=expires
            )
            return url
        except S3Error as e:
            logger.error(f"Error generating presigned URL: {e}")
            raise

    def get_object_url(self, object_name):
        try:
            url = f"http://{settings.MINIO_ENDPOINT}/{self.bucket_name}/{urllib.parse.quote(object_name)}"
            return url
        except Exception as e:
            logger.error(f"Error generating object URL: {e}")
            raise
