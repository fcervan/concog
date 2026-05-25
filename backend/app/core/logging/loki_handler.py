import os
import json
import logging
import requests
from datetime import datetime, timezone

class LokiHandler(logging.Handler):
    def __init__(self, loki_url=None, labels=None):
        super().__init__()
        self.loki_url = loki_url or os.getenv("LOKI_URL", "http://localhost:3100/loki/api/v1/push")
        self.labels = labels or {
            "app": os.getenv("APP_NAME", "concog"),
            "env": os.getenv("ENV", "local"),
        }

    def emit(self, record):
        try:
            log_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": self.format(record),
            }
            if record.exc_info and record.exc_info[0]:
                log_entry["exception"] = self.format(record)

            labels = {**self.labels}
            extra_labels = getattr(record, "loki_labels", None)
            if extra_labels:
                labels.update(extra_labels)

            payload = {
                "streams": [
                    {
                        "stream": labels,
                        "values": [
                            [str(int(datetime.now(timezone.utc).timestamp() * 1e9)), json.dumps(log_entry)]
                        ]
                    }
                ]
            }
            resp = requests.post(self.loki_url, json=payload, timeout=5)
            if resp.status_code != 204:
                print(f"[Loki] Erro ao enviar log: {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"[Loki] Falha ao enviar log: {e}")
            import traceback
            traceback.print_exc()

def setup_loki_logger(name="concog", level=logging.INFO, extra_labels=None):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    handler = LokiHandler(labels={**{"app": name}, **(extra_labels or {})})
    handler.setFormatter(logging.Formatter("%(levelname)s - %(name)s - %(message)s"))
    logger.addHandler(handler)

    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter("%(levelname)s - %(name)s - %(message)s"))
    logger.addHandler(console)

    return logger
