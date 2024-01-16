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


def delete_users(event: any, context: any) -> dict:
    """
    FUNCIÓN PARA ELIMINAR UN USUARIO EN LA TABLA USERS
    """
    logger.info(f"EVENT --> {event}")
    table_users_put = dynamo_table_name("usersTable", str(is_offline))

    # BÚSQUEDA QUE EXISTA ITEM A ELIMINAR
    # item_found = table_users_put.query(
    #     KeyConditionExpression=Key("pk").eq(event["body"]["pk"])
    # )

    # if len(item_found["Items"]) == 0:
    #     return (422, "Item no existe.")

    logger.info(f"PATHPARAMETERS_ID --> {event['pathParameters']['id']}")

    # ELIMINACIÓN DEL ITEM
    response = table_users_put.delete_item(Key={"pk": event["pathParameters"]["id"]})

    logger.info(f"RESPONSE --> {response}")

    if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
        return {
            "statusCode": response["ResponseMetadata"]["HTTPStatusCode"],
            "body": json.dumps({"message": "Item deleted successfully"}),
        }
    else:
        return {
            "statusCode": response["ResponseMetadata"]["HTTPStatusCode"],
            "body": json.dumps({"message": "Error deleting item"}),
        }
