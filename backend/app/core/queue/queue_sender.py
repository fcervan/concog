import os
import json
import boto3
from redis import Redis
from rq import Queue
from datetime import datetime
from urllib.parse import unquote

class QueueSender:
    def __init__(self):
        self.env = os.getenv("ENV", "local")
        self._init_queue()

    def _init_queue(self):
        if self.env == "local":
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            redis_conn = Redis.from_url(redis_url)
            queue_name = os.getenv("QUEUE_SPLITAR_LANCAMENTO", "cc-splitar-lancamento")
            self.queue = Queue(queue_name, connection=redis_conn)
        else:
            self.sqs = boto3.client(
                "sqs",
                region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
            )

    def send_splitar_lancamento(self, s3_path: str):
        mensagem = self._build_s3_event(s3_path)

        if self.env == "local":
            from app.jobs.splitar_lancamento_job import processar_splitar
            self.queue.enqueue(processar_splitar, mensagem)
        else:
            queue_url = os.getenv("SQS_SPLITAR_LANCAMENTO_URL")
            if not queue_url:
                raise ValueError("SQS_SPLITAR_LANCAMENTO_URL não configurada")
            self.sqs.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps(mensagem)
            )

    def _build_s3_event(self, s3_path: str) -> dict:
        return {
            'Records': [{
                'eventVersion': '2.1',
                'eventSource': 'aws:s3',
                'awsRegion': os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
                'eventTime': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')[:-3] + 'Z',
                'eventName': 'ObjectCreated:Put',
                'userIdentity': {'principalId': 'AIDAJDPLRKLG7UEXAMPLE'},
                'requestParameters': {'sourceIPAddress': '127.0.0.1'},
                'responseElements': {
                    'x-amz-request-id': '96b9509a',
                    'x-amz-id-2': 'eftixk72aD6Ap51TnqcoF8eFidJG9Z/2'
                },
                's3': {
                    's3SchemaVersion': '1.0',
                    'configurationId': 'trigger-xlsx-arquivo-original',
                    'bucket': {
                        'name': 'concog',
                        'ownerIdentity': {'principalId': 'A3NL1KOZZKExample'},
                        'arn': 'arn:aws:s3:::concog'
                    },
                    'object': {
                        'key': unquote(s3_path),
                        'sequencer': '0055AED6DCD90281E5',
                        'eTag': '1f76dd5472649005af5d98155d47af09',
                        'size': 0
                    }
                }
            }]
        }

queue_sender = QueueSender()
