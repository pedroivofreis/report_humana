"""S3 utility module for file upload and management."""

import uuid
from typing import Any

import boto3
import structlog
from botocore.exceptions import ClientError
from fastapi import UploadFile

from app.core.config import settings

logger = structlog.get_logger(__name__)


class S3Service:
    """S3 service for file operations."""

    def __init__(self) -> None:
        """Initialize S3 client with credentials from settings."""
        client_config = {
            "service_name": "s3",
            "aws_access_key_id": settings.AWS_ACCESS_KEY_ID,
            "aws_secret_access_key": settings.AWS_SECRET_ACCESS_KEY,
            "region_name": settings.AWS_REGION,
        }

        if settings.S3_ENDPOINT_URL and settings.S3_ENDPOINT_URL.strip():
            client_config["endpoint_url"] = settings.S3_ENDPOINT_URL

        self.s3_client = boto3.client(**client_config)
        self.bucket_name = settings.S3_BUCKET_NAME

    async def upload_file(self, file: UploadFile, folder: str = "documents") -> str:
        """
        Upload file to S3 bucket.

        Args:
            file: UploadFile from FastAPI
            folder: Folder path in S3 bucket

        Returns:
            str: Public URL of uploaded file

        Raises:
            Exception: If upload fails
        """
        try:
            # Generate unique filename
            file_extension = file.filename.split(".")[-1] if file.filename else "bin"
            unique_filename = f"{folder}/{uuid.uuid4()}.{file_extension}"

            # Read file content
            file_content = await file.read()

            # Reset file pointer
            await file.seek(0)

            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=unique_filename,
                Body=file_content,
                ContentType=file.content_type or "application/octet-stream",
            )

            if settings.S3_ENDPOINT_URL:
                file_url = f"{settings.S3_ENDPOINT_URL}/{self.bucket_name}/{unique_filename}"
            else:
                file_url = f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{unique_filename}"

            logger.info("File uploaded to S3", filename=unique_filename, url=file_url)

            return file_url

        except ClientError as e:
            logger.error("Failed to upload file to S3", error=str(e))
            raise Exception(f"Failed to upload file to S3: {str(e)}") from e

    async def upload_file_return_key(self, file: UploadFile, folder: str = "documents") -> tuple[str, str]:
        """
        Upload file to S3 bucket and return both URL and Key.

        Args:
            file: UploadFile from FastAPI
            folder: Folder path in S3 bucket

        Returns:
            tuple[str, str]: Public URL, Key of uploaded file

        Raises:
            Exception: If upload fails
        """
        try:
            file_extension = file.filename.split(".")[-1] if file.filename else "bin"
            unique_filename = f"{folder}/{uuid.uuid4()}.{file_extension}"
            file_content = await file.read()
            await file.seek(0)
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=unique_filename,
                Body=file_content,
                ContentType=file.content_type or "application/octet-stream",
            )
            if settings.S3_ENDPOINT_URL:
                file_url = f"{settings.S3_ENDPOINT_URL}/{self.bucket_name}/{unique_filename}"
            else:
                file_url = f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{unique_filename}"
            logger.info("File uploaded to S3", filename=unique_filename, url=file_url)
            return file_url, unique_filename

        except ClientError as e:
            logger.error("Failed to upload file to S3", error=str(e))
            raise Exception(f"Failed to upload file to S3: {str(e)}") from e

    def delete_file(self, file_url: str) -> bool:
        """
        Delete file from S3 bucket.

        Args:
            file_url: Full URL of the file to delete

        Returns:
            bool: True if deletion was successful

        Raises:
            Exception: If deletion fails
        """
        try:
            if settings.S3_ENDPOINT_URL:
                key = file_url.replace(f"{settings.S3_ENDPOINT_URL}/{self.bucket_name}/", "")
            else:
                key = file_url.split(f"{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/")[
                    -1
                ]

            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)

            logger.info("File deleted from S3", key=key)

            return True

        except ClientError as e:
            logger.error("Failed to delete file from S3", error=str(e))
            raise Exception(f"Failed to delete file from S3: {str(e)}") from e

    def delete_file_by_key(self, key: str) -> bool:
        """
        Delete file from S3 bucket by key.

        Args:
            key: Key of the file to delete

        Returns:
            bool: True if deletion was successful

        Raises:
            Exception: If deletion fails
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            logger.info("File deleted from S3", key=key)
            return True
        except ClientError as e:
            logger.error("Failed to delete file from S3", error=str(e))
            raise Exception(f"Failed to delete file from S3 by key: {str(e)}") from e

    def get_presigned_url(self, file_url: str, expiration: int = 3600) -> str:
        """
        Generate presigned URL for private files.

        Args:
            file_url: Full URL of the file
            expiration: URL expiration time in seconds (default 1 hour)

        Returns:
            str: Presigned URL
        """
        try:
            if settings.S3_ENDPOINT_URL:
                key = file_url.replace(f"{settings.S3_ENDPOINT_URL}/{self.bucket_name}/", "")
            else:
                key = file_url.split(f"{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/")[
                    -1
                ]

            presigned_url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": key},
                ExpiresIn=expiration,
            )

            return str(presigned_url)

        except ClientError as e:
            logger.error("Failed to generate presigned URL", error=str(e))
            raise Exception(f"Failed to generate presigned URL: {str(e)}") from e

    async def upload_fileobj(self, file_obj: Any, key: str, content_type: str | None = None) -> str:
        """
        Upload a file-like object to S3.
        """
        try:
            extra_args = {}
            if content_type:
                extra_args["ContentType"] = content_type

            self.s3_client.upload_fileobj(file_obj, self.bucket_name, key, ExtraArgs=extra_args)

            if settings.S3_ENDPOINT_URL:
                file_url = f"{settings.S3_ENDPOINT_URL}/{self.bucket_name}/{key}"
            else:
                file_url = (
                    f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"
                )

            logger.info("File object uploaded to S3", key=key, url=file_url)
            return file_url

        except ClientError as e:
            logger.error("Failed to upload file object to S3", error=str(e))
            raise Exception(f"Failed to upload file object to S3: {str(e)}") from e

    def get_object_url(self, key: str) -> str:
        """Get public URL for a key."""
        if settings.S3_ENDPOINT_URL:
            return f"{settings.S3_ENDPOINT_URL}/{self.bucket_name}/{key}"
        return f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"

    def download_to_tempfile(self, key: str) -> str:
        """
        Download S3 object to a temporary file and return the path.
        """
        import os
        import tempfile

        try:
            # Create temp file
            suffix = os.path.splitext(key)[1] if "." in key else ""
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                self.s3_client.download_fileobj(self.bucket_name, key, tmp)
                return tmp.name
        except ClientError as e:
            logger.error("Failed to download file from S3", error=str(e))
            raise Exception(f"Failed to download file from S3: {str(e)}") from e


# Singleton instance
s3_service = S3Service()
