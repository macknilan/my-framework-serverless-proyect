import json
import logging
import os
import sys
import uuid
from datetime import datetime, timedelta
from typing import Any
from urllib.parse import unquote_plus

import boto3
import PIL.Image
from PIL import Image

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

S3_CLIENT = boto3.client("s3")

is_offline = os.environ.get(
    "IS_OFFLINE"
)  # VARIABLE DE ENTORNO PARA SABER SI SE ESTÁ EN LOCAL O EN LA NUBE

# OBTENER LA FECHA Y HORA ACTUAL EN UTC
now_utc = datetime.utcnow()

# EXTRAER 6 HORAS PARA OBTENER LA FECHA Y HORA ACTUAL EN UTC-6
now_utc_6 = now_utc - timedelta(hours=6)

# OBTENER EL AÑO, MES Y DÍA ANTERIOR AL ACTUAL EN UTC-6
current_year: int = now_utc_6.year
current_month: str = str(now_utc_6.month).zfill(2)
current_day: str = str(now_utc_6.day).zfill(2)
current_second: str = str(now_utc_6.second)


def resize_save(
    bucket_name: str, file_name: str, file_extension: str, original_image: Any, image_size: int
):
    """
    RE-DIMENSIONAR UNA IMAGEN Y GUARDARLA EN UNA CARPETA DIFERENTE DENTRO DEL BUCKET
    """
    logger.info(f"IMAGE_SIZE --> {image_size}")

    image = original_image.copy()  # SE CREA COPIA DE LA IMAGEN ORIGINAL

    image.thumbnail((image_size, image_size))
    image.save(
        f"/tmp/{file_name}_{current_year}{current_month}{current_day}{current_second}_{image_size}{file_extension}"
    )

    S3_CLIENT.upload_file(
        f"/tmp/{file_name}_{current_year}{current_month}{current_day}{current_second}_{image_size}{file_extension}",
        bucket_name,
        f"resized/{file_name}_{current_year}{current_month}{current_day}{current_second}_{image_size}{file_extension}",
    )

    response = S3_CLIENT.head_object(
        Bucket=bucket_name,
        Key=f"resized/{file_name}_{current_year}{current_month}{current_day}{current_second}_{image_size}{file_extension}",
    )
    logger.info(f"RESPONSE_UPLOAD_FILE --> {file_name}_{current_year}{current_month}{current_day}{current_second}_{image_size}{file_extension}: {response['ResponseMetadata']['HTTPStatusCode']}")


def thumbnail_generator(event: any, context: any) -> Any:
    """
    GENERAR TRES THUMBNAILS DE UNA IMAGEN SUBIDA A S3
    Y GUARDARLOS EN UNA CARPETA DIFERENTE DENTRO DEL BUCKET
    """
    logger.info(f"EVENT --> {event}")

    # GET THE BUCKET NAME
    bucket_name: str = event["Records"][0]["s3"]["bucket"]["name"]
    logger.info(f"BUCKET_NAME --> {bucket_name}")

    # GET THE FILE NAME UPLOADED AND EXTENSION
    # https://docs.python.org/3/library/os.path.html?highlight=splitext#os.path.splitext
    s3_key_name_file, s3_key_name_file_extension = os.path.splitext(
        event["Records"][0]["s3"]["object"]["key"]
    )
    logger.info(f"S3_PATH_NAME --> {s3_key_name_file}")

    key_name_file: str = s3_key_name_file[s3_key_name_file.find("/") + 1 :]
    key_name_file: str = unquote_plus(key_name_file)
    key_name_file: str = key_name_file.replace(" ", "_").lower()

    logger.info(f"FILE_NAME --> {key_name_file}")
    logger.info(f"FILE_EXTENSION --> {s3_key_name_file_extension}")
    logger.info(f"FILE --> {key_name_file}{s3_key_name_file_extension}")

    if s3_key_name_file_extension == ".jpg" or s3_key_name_file_extension == ".png":
        response_get_object = S3_CLIENT.get_object(
            Bucket=bucket_name,
            Key=f"upload/{key_name_file}{s3_key_name_file_extension}",
        )
        logger.info(f"RESPONSE_GET_OBJECT[Body] --> {response_get_object}")

        with Image.open(response_get_object["Body"]) as image:
            widths: list[int] = [50, 100, 200]

            for image_size in widths:
                resize_save(
                    bucket_name,
                    f"{key_name_file}",
                    f"{s3_key_name_file_extension}",
                    image,
                    image_size
                )

    else:
        logger.info(f"{s3_key_name_file_extension} file extension not allowed.")

    return {"statusCode": 200, "body": "OK"}
