import logging
import os
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# OBTENER LA FECHA Y HORA ACTUAL EN UTC
now_utc = datetime.utcnow()

# EXTRAER 6 HORAS PARA OBTENER LA FECHA Y HORA ACTUAL EN UTC-6
now_utc_6 = now_utc - timedelta(hours=6)

# OBTENER EL HORA Y MINUTO ANTERIOR AL ACTUAL EN UTC-6
current_hour: str = str(now_utc_6.hour).zfill(2)
current_minute: str = str(now_utc_6.minute).zfill(2)


def authorize(event: any, context: any) -> Any:
    """
    FUNCIÓN PARA AUTORIZAR UN USUARIO MEDIANTE UN CUSTOM AUTHORIZER
    """
    logger.info(f"EVENT --> {event}")
    logger.info(f"OS --> {os.environ}")

    logger.info(f"CURRENT_MINUTE --> {current_minute}")
    logger.info(f"CURRENT_HOUR --> {current_hour}")

    expected_token = f"{os.environ.get('SECRET_EEG')}-{current_hour}-{current_minute}"
    logger.info(f"Expected token: Bearer {expected_token}")

    if event.get("authorizationToken", "").strip().startswith("Bearer "):
        provided_token = event["authorizationToken"][7:]  # Remove 'Bearer ' from the start
    else:
        provided_token = event.get("authorizationToken", "")

    if provided_token == expected_token:
        return {
            "principalId": "anonymous",
            "policyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Action": "execute-api:Invoke",
                        "Effect": "Allow",
                        "Resource": event["methodArn"],
                    }
                ],
            },
        }
    else:
        return {
            "message": "Unauthorized",
        }






