import base64
import uuid
from typing import Optional
import boto3
from botocore.client import Config
from app.core.config import get_settings


class CloudflareR2Service:
    """Service để upload HTML tables và images lên Cloudflare R2"""

    def __init__(self):
        self.settings = get_settings()
        self.s3_client = self._init_s3_client()

    def _init_s3_client(self):
        """Initialize S3 client với Cloudflare R2 credentials"""
        if not all([
            self.settings.CLOUDFLARE_ACCOUNT_ID,
            self.settings.CLOUDFLARE_ACCESS_KEY,
            self.settings.CLOUDFLARE_SECRET_KEY
        ]):
            raise ValueError("Cloudflare R2 credentials not configured in .env file")

        s3_client = boto3.client(
            "s3",
            endpoint_url=f"https://{self.settings.CLOUDFLARE_ACCOUNT_ID}.r2.cloudflarestorage.com",
            aws_access_key_id=self.settings.CLOUDFLARE_ACCESS_KEY,
            aws_secret_access_key=self.settings.CLOUDFLARE_SECRET_KEY,
            config=Config(signature_version="s3v4"),
            region_name="auto"
        )
        return s3_client

    def upload_image_from_base64(self, image_b64: str, filename: Optional[str] = None) -> str:
        """
        Upload base64 image lên R2 và trả về public URL
        
        Args:
            image_b64: Base64 encoded image data (có thể có data:image/... prefix)
            filename: Tên file (nếu không có sẽ auto-generate)
            
        Returns:
            Public URL của image
        """
        if not image_b64:
            return ""

        # Remove data URL prefix nếu có
        if "," in image_b64:
            image_b64 = image_b64.split(",")[1]

        # Decode base64 to binary
        try:
            image_data = base64.b64decode(image_b64)
        except Exception as e:
            raise ValueError(f"Invalid base64 image data: {e}")

        # Generate filename nếu không có
        if not filename:
            filename = f"images/{uuid.uuid4()}.png"
        elif not filename.startswith("images/"):
            filename = f"images/{filename}"

        # Upload to R2
        try:
            self.s3_client.put_object(
                Bucket=self.settings.CLOUDFLARE_BUCKET_NAME,
                Key=filename,
                Body=image_data,
                ContentType="image/png"
            )

            # Return public URL
            return self._get_public_url(filename)

        except Exception as e:
            raise RuntimeError(f"Failed to upload image to R2: {e}")

    def upload_html_table(self, html_content: str, filename: Optional[str] = None) -> str:
        """
        Upload HTML table lên R2 và trả về public URL
        
        Args:
            html_content: HTML content của table
            filename: Tên file (nếu không có sẽ auto-generate)
            
        Returns:
            Public URL của HTML table
        """
        if not html_content:
            return ""

        # Generate filename nếu không có
        if not filename:
            filename = f"tables/{uuid.uuid4()}.html"
        elif not filename.startswith("tables/"):
            filename = f"tables/{filename}"

        # Upload to R2
        try:
            self.s3_client.put_object(
                Bucket=self.settings.CLOUDFLARE_BUCKET_NAME,
                Key=filename,
                Body=html_content.encode('utf-8'),
                ContentType="text/html; charset=utf-8"
            )

            # Return public URL
            return self._get_public_url(filename)

        except Exception as e:
            raise RuntimeError(f"Failed to upload HTML table to R2: {e}")

    def _get_public_url(self, filename: str) -> str:
        """Generate public URL cho file"""
        if self.settings.CLOUDFLARE_PUBLIC_URL:
            # Use custom domain nếu có
            return f"{self.settings.CLOUDFLARE_PUBLIC_URL.rstrip('/')}/{filename}"
        else:
            # Use R2 public URL
            return f"https://{self.settings.CLOUDFLARE_BUCKET_NAME}.{self.settings.CLOUDFLARE_ACCOUNT_ID}.r2.cloudflarestorage.com/{filename}"

    def delete_file(self, filename: str) -> bool:
        """Xóa file khỏi R2"""
        try:
            self.s3_client.delete_object(
                Bucket=self.settings.CLOUDFLARE_BUCKET_NAME,
                Key=filename
            )
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to delete file from R2: {e}")

    def list_files(self, prefix: str = "") -> list[str]:
        """List tất cả files trong R2 bucket"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.settings.CLOUDFLARE_BUCKET_NAME,
                Prefix=prefix
            )
            files = []
            if "Contents" in response:
                files = [obj["Key"] for obj in response["Contents"]]
            return files
        except Exception as e:
            raise RuntimeError(f"Failed to list files from R2: {e}")
