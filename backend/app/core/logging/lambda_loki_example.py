import os
import json
import requests
from datetime import datetime

LOKI_URL = os.getenv("LOKI_URL", "http://seu-ec2-ip:3100/loki/api/v1/push")

def log_to_loki(level, message, extra=None):
    labels = {
        "app": "concog-lambda",
        "env": os.getenv("ENV", "prod"),
        "component": "lambda",
        "function": os.getenv("AWS_LAMBDA_FUNCTION_NAME", "unknown"),
    }
    if extra:
        labels.update(extra)

    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "level": level,
        "message": message,
    }

    payload = {
        "streams": [
            {
                "stream": labels,
                "values": [
                    [str(int(datetime.utcnow().timestamp() * 1e9)), json.dumps(log_entry)]
                ]
            }
        ]
    }

    try:
        requests.post(LOKI_URL, json=payload, timeout=5)
    except Exception:
        pass

def handler(event, context):
    log_to_loki("INFO", "Lambda invocado", {"request_id": context.aws_request_id})

    try:
        resultado = processar(event)
        log_to_loki("INFO", "Lambda concluido com sucesso")
        return {"statusCode": 200, "body": json.dumps(resultado)}
    except Exception as e:
        log_to_loki("ERROR", f"Lambda falhou: {str(e)}")
        raise

def processar(event):
    log_to_loki("INFO", "Iniciando processamento")
    return {"status": "ok"}
