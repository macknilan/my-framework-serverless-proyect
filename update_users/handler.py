import json
import logging
import os
from decimal import Decimal
from json import JSONEncoder
from typing import Any, Dict, Union

import boto3
from boto3.dynamodb.conditions import Key

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

is_offline = os.environ.get(
    "IS_OFFLINE"
)  # VARIABLE DE ENTORNO PARA SABER SI SE ESTÁ EN LOCAL O EN LA NUBE


class DecimalEncoder(JSONEncoder):
    """
    SERIALIZAR OBJETOS PYTHON A JSON
    """

    def default(self, obj):
        # 👇️ SI EL OBJETO ES UNA INSTANCIA DE DECIMAL
        # SE CONVIERTE A ENTERO
        if isinstance(obj, Decimal):
            return int(obj)

        return JSONEncoder.default(self, obj)


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


def update_users(event: any, context: any) -> Dict[str, Union[str, int]]:
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
        UpdateExpression="SET #name = :val1, \
            #age = :val2, \
            #email = :val3",
        ExpressionAttributeNames={
            "#name": "name",
            "#age": "age",
            "#email": "email",
        },
        ExpressionAttributeValues={
            ":val1": pre_payload["name"],
            ":val2": pre_payload["age"],
            ":val3": pre_payload["email"],
        },
        ReturnValues="ALL_NEW",
    )

    logger.info(f"RESPONSE --> {response}")

    if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
        return {
            "statusCode": 200,
            "body": json.dumps(response["Attributes"], cls=DecimalEncoder),
        }
    else:
        return {"statusCode": 200, "body": {}}
