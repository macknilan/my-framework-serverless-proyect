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


def update_users(event: any, context: any) -> dict:
    """
    FUNCIÓN PARA ACTUALIZAR UN USUARIO EN LA TABLA USERS
    """
    logger.info(f"EVENT --> {event}")
    table_users_put = dynamo_table_name("usersTable", str(is_offline))

    # BÚSQUEDA QUE EXISTA ITEM A ACTUALIZAR
    # item_found = table_users_put.query(
    #     KeyConditionExpression=Key("pk").eq(event["body"]["pk"])
    # )

    # if len(item_found["Items"]) == 0:
    #     return (422, "Item no existe.")

    pre_payload = json.loads(event["body"])
    logger.info(f"PRE_PAYLOAD --> {pre_payload}")

    logger.info(f"PATHPARAMETERS_ID --> {event['pathParameters']['id']}")

    # ACTUALIZACIÓN DEL ITEM
    response = table_users_put.update_item(
        Key={"pk": event["pathParameters"]["id"]},
        UpdateExpression="SET #nombre = :val1, \
            #telefono = :val2",
        ExpressionAttributeNames={
            "#nombre": "nombre",
            "#telefono": "telefono",
        },
        ExpressionAttributeValues={
            ":val1": pre_payload["nombre"],
            ":val2": pre_payload["telefono"],
        },
        ReturnValues="ALL_NEW",
    )

    logger.info(f"RESPONSE --> {response}")

    if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
        return {"statusCode": 200, "body": json.dumps(response["Attributes"])}
    else:
        return {"statusCode": 200, "body": {}}
