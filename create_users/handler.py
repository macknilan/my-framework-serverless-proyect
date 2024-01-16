import json
import logging
import os
import uuid
from typing import Any

import boto3
from boto3.dynamodb.conditions import Key

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

is_offline = os.environ.get(
    "IS_OFFLINE"
)  # VARIABLE DE ENTORNO PARA SABER SI SE ESTÁ EN LOCAL O EN LA NUBE


def dynamo_table_name(t: str, is_offline: str) -> Any:
    """
    FUNCIÓN PARA SELECCIONAR LA TABLA EN DYNAMODB
    """
    if is_offline:
        _DYNAMODB = boto3.resource(
            "dynamodb",
            region_name="localhost",
            endpoint_url="http://localhost:8000",
        )
    if is_offline == "None":
        _DYNAMODB = boto3.resource("dynamodb")

    _table_selected = _DYNAMODB.Table(t)

    return _table_selected


def create_users(event: any, context: any) -> dict:
    """
    FUNCIÓN PARA CREAR UN USUARIO EN LA TABLA USERS
    """

    logger.info(f"EVENT --> {event}")

    table_users_post = dynamo_table_name("usersTable", str(is_offline))

    pre_payload = json.loads(event["body"])
    payload: dict[str, str] = {
        "pk": str(uuid.uuid4()),
        "nombre": pre_payload["nombre"],
        "telefono": pre_payload["telefono"],
    }

    # INSERCIÓN DEL ITEM
    table_users_post = dynamo_table_name("usersTable", str(is_offline))
    response = table_users_post.put_item(Item=payload)

    if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
        return {"statusCode": 200, "body": json.dumps(payload)}
    else:
        return {"statusCode": 200, "body": {}}
