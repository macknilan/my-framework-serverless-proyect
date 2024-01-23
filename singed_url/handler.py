import json
import logging
import os
from typing import Any

import boto3
from boto3.dynamodb.conditions import Key

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

S3_CLIENT = boto3.client("s3")

is_offline = os.environ.get(
    "IS_OFFLINE"
)  # VARIABLE DE ENTORNO PARA SABER SI SE ESTÁ EN LOCAL O EN LA NUBE


def singed_url(event: any, context: any) -> Any:
    """
    GENERAR UNA URL PRE-FIRMADA PARA SUBIR UN OBJETO S3
    """

    logger.info(f"EVENT --> {event}")
    file_name: str = str(event["queryStringParameters"]["filename"])
    file_extension = os.path.splitext(file_name)[1]
    logger.info(f"FILE_NAME_QRY_STR --> {file_name}")
    logger.info(f"FILE_EXTENSION --> {file_extension}")

    # REVISAR SI LA EXTENSIÓN DEL ARCHIVO ES .png or .jpg
    if file_extension not in ['.png', '.jpg']:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid file type. Only .png and .jpg files are allowed."}),
        }

    file_name: str = str(event["queryStringParameters"]["filename"])
    logger.info(f"FILE_NAME_QRY_STR --> {file_name}")

    logger.info(f"BUCKET --> {os.environ.get('BUCKET')}")

    # GENERAR URL PRE-FIRMADA
    response_presigned_url: str = S3_CLIENT.generate_presigned_post(
        Bucket=os.environ.get("BUCKET"),
        Key=f"upload/{file_name}",
        ExpiresIn=600,  # TIEMPO DE EXPIRACIÓN DE LA URL EN SEGUNDOS (150s = 2.5min)
        Conditions=[
            ["content-length-range", 0, 1024 * 1024]  # TAMAÑO LIMITE DE ARCHIVO 1MB
        ]
    )

    logger.info(f"RESPONSE_PRESIGNED_URL --> {response_presigned_url}")

    return {
        "statusCode": 200,
        "body": json.dumps({"singed_url": response_presigned_url}),
    }
