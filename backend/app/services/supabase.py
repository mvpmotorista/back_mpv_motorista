from io import BytesIO
from typing import Optional
from uuid import uuid4

import httpx

from app.core.config import settings


class SupabaseStorageService:
    def __init__(
        self,
    ):
        self.supabase_url = settings.SUPABASE_URL.rstrip("/")
        self.supabase_key = settings.SUPABASE_KEY
        self.bucket_name = settings.BUKCET_ABRASILEIRAR

    def upload_fileobj(self, file_obj, key: Optional[str] = None, content_type: Optional[str] = None):
        try:
            key = key or f"{uuid4()}"
            content_type = content_type or "application/octet-stream"
            buffer = BytesIO(file_obj.file.read())
            buffer.seek(0)
            file_bytes = buffer.read()

            headers = {
                "Authorization": f"Bearer {self.supabase_key}",
                "Content-Type": content_type,
                "x-upsert": "true",  # sobrescreve se já existir
            }

            path = f"{self.bucket_name}/{key}"
            url = f"{self.supabase_url}/storage/v1/object/{path}"

            response = httpx.post(url, headers=headers, content=file_bytes)

            if response.status_code in (200, 201):
                public_url = f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{key}"
                return {"success": True, "key": key, "url": public_url, 'path': key}
            else:
                return {"success": False, "status": response.status_code, "error": response.text}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def url_builder(self, key: str | None) -> Optional[str]:
        if not key:
            return None
        public_url = f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{key}"
        return public_url
    
    def dowload_file(self, key: str) -> Optional[bytes]:
        try:
            path = f"{self.bucket_name}/{key}"
            url = f"{self.supabase_url}/storage/v1/object/{path}"
            headers = {
                "Authorization": f"Bearer {self.supabase_key}",
            }
            response = httpx.get(url, headers=headers)
            if response.status_code == 200:
                return response.content
            else:
                return None
        except Exception as e:
            return None


url_builder = SupabaseStorageService().url_builder
