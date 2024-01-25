import json
import logging
from decimal import Decimal
from json import JSONEncoder
from typing import Any

import boto3

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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


def dynamo_table_name(t: str) -> Any:
    """
    FUNCIÓN PARA SELECCIONAR LA TABLA EN DYNAMODB
    """
    _DYNAMODB = boto3.resource("dynamodb")
    _table_selected = _DYNAMODB.Table(t)

    return _table_selected


def like_user(event: any, context: any) -> Any:
    """
    FUNCIÓN PARA DAR LIKE A UN USUARIO
    MEDIANTE EL TRIGGER SQS EN LA LAMBDA
    """
    logger.info(f"EVENT --> {event}")
    pre_payload = json.loads(event["Records"][0]["body"])
    logger.info(f"PRE_PAYLOAD --> {pre_payload}")

    # ACTUALIZACIÓN DEL ITEM
    table_users_put = dynamo_table_name("usersTable")
    response = table_users_put.update_item(
        Key={"pk": pre_payload["id"]},
        UpdateExpression="ADD likes :val1",
        ExpressionAttributeValues={":val1": 1},
        ReturnValues="ALL_NEW"
    )
    logger.info(f"RESPONSE --> {response}")

    if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
        return {
            "statusCode": 200,
            "body": json.dumps(response["Attributes"], cls=DecimalEncoder),
        }
    else:
        return {"statusCode": 200, "body": {}}
