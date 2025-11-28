import os
import boto3
from fastapi import File, UploadFile, APIRouter
from botocore.exceptions import NoCredentialsError
from configuration.environments import AWS_DEFAULT_BUCKET,AWS_DEFAULT_REGION,AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY


router = APIRouter()

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_DEFAULT_REGION
)


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        return {"error": "Solo se permiten archivos PDF"}

    try:
        s3_client.upload_fileobj(
        file.file,
        AWS_DEFAULT_BUCKET,
        file.filename,
        ExtraArgs={"ContentType": "application/pdf"}
    )

        file_url = f"https://{AWS_DEFAULT_BUCKET}.s3.{AWS_DEFAULT_REGION}.amazonaws.com/{file.filename}"
        return {"success": True, "url": file_url}

    except NoCredentialsError:
        return {"error": "Credenciales de AWS no configuradas"}
    except Exception as e:
        return {"error": str(e)}