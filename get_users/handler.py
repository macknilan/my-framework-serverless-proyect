import json
import logging
import os
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


def get_users(event: any, context: any) -> dict:
    """
    FUNCIÓN PARA OBTENER LOS USUARIOS DE LA TABLA USERS
    """

    logger.info(f"EVENT --> {event}")

    table_users_get = dynamo_table_name("usersTable", str(is_offline))

    user_id: str = str(event["pathParameters"]["id"])

    # OBTENER EL ITEM
    response = table_users_get.query(KeyConditionExpression=Key("pk").eq(user_id))
    result = response["Items"]

    return {"statusCode": 200, "body": json.dumps(result)}
