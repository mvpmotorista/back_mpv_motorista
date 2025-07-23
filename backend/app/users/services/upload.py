import logging
from typing import Optional

# import boto3
# from botocore.exceptions import ClientError

from app.core.config import settings


class S3Service:
    def __init__(
        self,
    ):
        self.bucket_name = settings.BUKCET_ABRASILEIRAR
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_DEFAULT_REGION,
            endpoint_url=settings.AWS_ENPOINT,
        )

    # def upload_fileobj(self, file_obj, key: str, content_type: Optional[str] = None):
    #     try:
    #         extra_args = {"ContentType": content_type} if content_type else {}
    #         from io import BytesIO
    #         buffer=BytesIO(file_obj.file.read())
    #         buffer.seek(0)
    #         self.s3_client.upload_fileobj(buffer, self.bucket_name, key, ExtraArgs=extra_args)
    #         return {"success": True, "key": key}
    #     except ClientError as e:
    #         raise e
    #         logging.error(e)
    #         return {"success": False, "error": str(e)}
    def upload_fileobj(self, file_obj, key: str, content_type: Optional[str] = None):
        try:
            extra_args = {"ContentType": content_type} if content_type else {}
            with open('/home/hian/Downloads/3874-controle-de-qualidade-testes.jpg', 'rb') as f:
                self.s3_client.upload_fileobj(f, self.bucket_name, key, ExtraArgs=extra_args)
                return {"success": True, "key": key}
        except ClientError as e:
            raise e
            logging.error(e)
            return {"success": False, "error": str(e)}

    def download_fileobj(self, key: str):
        try:
            file_obj = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            return file_obj["Body"]
        except ClientError as e:
            logging.error(e)
            return None

    def delete_file(self, key: str):
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            return {"success": True}
        except ClientError as e:
            logging.error(e)
            return {"success": False, "error": str(e)}

    def generate_presigned_url(self, key: str, expires_in: int = 3600):
        try:
            url = self.s3_client.generate_presigned_url(
                ClientMethod='get_object', Params={'Bucket': self.bucket_name, 'Key': key}, ExpiresIn=expires_in
            )
            return url
        except ClientError as e:
            logging.error(e)
            return None
