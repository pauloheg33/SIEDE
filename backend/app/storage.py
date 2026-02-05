import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from PIL import Image
import io
from uuid import uuid4
from typing import Optional

from app.config import get_settings


class StorageService:
    def __init__(self):
        settings = get_settings()
        self._configured = all([
            settings.S3_ENDPOINT_URL,
            settings.S3_ACCESS_KEY_ID,
            settings.S3_SECRET_ACCESS_KEY,
            settings.S3_BUCKET_NAME
        ])
        
        if self._configured:
            self.s3_client = boto3.client(
                's3',
                endpoint_url=settings.S3_ENDPOINT_URL,
                aws_access_key_id=settings.S3_ACCESS_KEY_ID,
                aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
                region_name=settings.S3_REGION,
                config=Config(signature_version='s3v4')
            )
            self.bucket_name = settings.S3_BUCKET_NAME
            self.endpoint_url = settings.S3_ENDPOINT_URL
        else:
            self.s3_client = None
            self.bucket_name = None
            self.endpoint_url = None
    
    def _check_configured(self):
        if not self._configured:
            raise Exception("Storage not configured. Set S3 environment variables.")
    
    def upload_file(self, file_content: bytes, filename: str, content_type: str) -> str:
        """Upload file to S3 and return URL"""
        self._check_configured()
        try:
            key = f"{uuid4()}_{filename}"
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=file_content,
                ContentType=content_type
            )
            # Generate URL
            url = f"{self.endpoint_url}/{self.bucket_name}/{key}"
            return url
        except ClientError as e:
            raise Exception(f"Failed to upload file: {str(e)}")
    
    def create_thumbnail(self, image_content: bytes, max_size: int = 320) -> bytes:
        """Create thumbnail from image"""
        try:
            img = Image.open(io.BytesIO(image_content))
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            output = io.BytesIO()
            # Save as JPEG for better compression
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            img.save(output, format='JPEG', quality=85)
            output.seek(0)
            return output.read()
        except Exception as e:
            raise Exception(f"Failed to create thumbnail: {str(e)}")
    
    def upload_photo_with_thumbnail(self, file_content: bytes, filename: str, content_type: str) -> tuple[str, str]:
        """Upload photo and its thumbnail, return both URLs"""
        # Upload original
        original_url = self.upload_file(file_content, filename, content_type)
        
        # Create and upload thumbnail
        try:
            thumbnail_content = self.create_thumbnail(file_content)
            thumbnail_filename = f"thumb_{filename}"
            thumbnail_url = self.upload_file(thumbnail_content, thumbnail_filename, "image/jpeg")
            return original_url, thumbnail_url
        except Exception as e:
            # If thumbnail fails, still return original
            print(f"Warning: Thumbnail creation failed: {str(e)}")
            return original_url, None
    
    def delete_file(self, url: str):
        """Delete file from S3 given its URL"""
        self._check_configured()
        try:
            # Extract key from URL
            key = url.split(f"{self.bucket_name}/")[-1]
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
        except ClientError as e:
            raise Exception(f"Failed to delete file: {str(e)}")
    
    def get_presigned_url(self, url: str, expiration: int = 3600) -> str:
        """Generate presigned URL for accessing file"""
        self._check_configured()
        try:
            key = url.split(f"{self.bucket_name}/")[-1]
            presigned_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': key},
                ExpiresIn=expiration
            )
            return presigned_url
        except ClientError as e:
            raise Exception(f"Failed to generate presigned URL: {str(e)}")


def get_storage_service():
    return StorageService()


storage_service = None


def init_storage():
    global storage_service
    storage_service = StorageService()
