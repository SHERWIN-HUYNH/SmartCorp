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
        self.bucket_name = self._get_required_setting("CLOUDFLARE_BUCKET_NAME")
        self.s3_client = self._init_s3_client()

    def _get_required_setting(self, key: str) -> str:
        value = getattr(self.settings, key, None)
        if value is None:
            raise ValueError(f"Missing required Cloudflare R2 env var: {key}")

        normalized = str(value).strip()
        if not normalized:
            raise ValueError(f"Missing required Cloudflare R2 env var: {key}")
        return normalized

    def _init_s3_client(self):
        """Initialize S3 client với Cloudflare R2 credentials"""
        required_keys = [
            "CLOUDFLARE_ACCOUNT_ID",
            "CLOUDFLARE_ACCESS_KEY",
            "CLOUDFLARE_SECRET_KEY",
            "CLOUDFLARE_BUCKET_NAME",
        ]
        missing_keys = []
        for key in required_keys:
            value = getattr(self.settings, key, None)
            if value is None or not str(value).strip():
                missing_keys.append(key)

        if missing_keys:
            missing_list = ", ".join(missing_keys)
            raise ValueError(f"Missing required Cloudflare R2 env var(s): {missing_list}")

        account_id = str(self.settings.CLOUDFLARE_ACCOUNT_ID).strip()
        access_key = str(self.settings.CLOUDFLARE_ACCESS_KEY).strip()
        secret_key = str(self.settings.CLOUDFLARE_SECRET_KEY).strip()

        s3_client = boto3.client(
            "s3",
            endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
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
                Bucket=self.bucket_name,
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
                Bucket=self.bucket_name,
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
            return f"https://{self.bucket_name}.{self.settings.CLOUDFLARE_ACCOUNT_ID}.r2.cloudflarestorage.com/{filename}"

    def delete_file(self, filename: str) -> bool:
        """Xóa file khỏi R2"""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=filename
            )
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to delete file from R2: {e}")

    def list_files(self, prefix: str = "") -> list[str]:
        """List tất cả files trong R2 bucket"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            files = []
            if "Contents" in response:
                files = [obj["Key"] for obj in response["Contents"]]
            return files
        except Exception as e:
            raise RuntimeError(f"Failed to list files from R2: {e}")
