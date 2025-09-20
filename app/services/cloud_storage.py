
import boto3
import os
from botocore.exceptions import NoCredentialsError
from fastapi import UploadFile
import uuid

class CloudStorage:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=os.environ.get('AWS_REGION', 'us-east-1')
        )
        self.bucket_name = os.environ.get('S3_BUCKET_NAME', 'sports-talent-videos')
    
    async def upload_video(self, file: UploadFile) -> str:
        """Upload video to cloud storage and return URL"""
        try:
            # Generate unique filename
            file_extension = file.filename.split('.')[-1]
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            
            # Upload file
            self.s3_client.upload_fileobj(
                file.file, 
                self.bucket_name, 
                unique_filename,
                ExtraArgs={'ContentType': file.content_type}
            )
            
            # Generate URL
            file_url = f"https://{self.bucket_name}.s3.amazonaws.com/{unique_filename}"
            return file_url
            
        except NoCredentialsError:
            raise Exception("AWS credentials not available")
        except Exception as e:
            raise Exception(f"Failed to upload file: {str(e)}")

# Fallback to local storage if cloud storage is not configured
async def save_upload_file(file: UploadFile, subdirectory: str = "") -> str:
    if all([os.environ.get('AWS_ACCESS_KEY_ID'), 
            os.environ.get('AWS_SECRET_ACCESS_KEY'),
            os.environ.get('S3_BUCKET_NAME')]):
        # Use cloud storage
        storage = CloudStorage()
        return await storage.upload_video(file)
    else:
        # Use local storage (for development)
        import shutil
        from pathlib import Path
        
        upload_dir = Path("uploads") / subdirectory
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / file.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return str(file_path)
