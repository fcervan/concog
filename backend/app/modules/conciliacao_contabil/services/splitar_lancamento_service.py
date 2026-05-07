import json
import os
import uuid
from urllib.parse import unquote

import boto3
from redis import Redis
from rq import Queue

from backend.app.modules.conciliacao_contabil.parsers.parser_factory import ParserFactory
from backend.app.modules.conciliacao_contabil.services.cliente_service import ClienteService
from backend.app.modules.conciliacao_contabil.services.lancamento_arquivo_service import LancamentoArquivoService
from backend.app.modules.conciliacao_contabil.services.lancamento_service import LancamentoService
from backend.app.core.database.unit_of_work import UnitOfWork
from backend.app.utils.datetime_utils import now_sp_str
from backend.app.jobs.processar_lancamento_job import processar_lancamento_job


class SplitarLancamentoService:

    def __init__(self):
        self.cliente = None

        self.env = os.getenv("ENV", "local").lower()

        self._configurar_storage()
        self._configurar_fila()

    def _configurar_storage(self):
        """
        Local:
            MinIO

        Produção:
            AWS S3
        """

        if self.env == "local":
            self.s3 = boto3.client(
                "s3",
                endpoint_url=os.getenv("MINIO_ENDPOINT"),
                aws_access_key_id=os.getenv("MINIO_ACCESS_KEY"),
                aws_secret_access_key=os.getenv("MINIO_SECRET_KEY"),
                region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
                config=boto3.session.Config(
                    s3={"addressing_style": "path"}
                )
            )
            return

        # produção
        self.s3 = boto3.client(
            "s3",
            region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        )

    def _configurar_fila(self):
        """
        Local:
            Redis + RQ

        Produção:
            AWS SQS
        """

        if self.env == "local":
            redis_url = os.getenv("REDIS_URL")

            if not redis_url:
                raise ValueError(
                    "REDIS_URL não configurada no ambiente local"
                )

            redis_conn = Redis.from_url(redis_url)

            queue_name = os.getenv(
                "QUEUE_PROCESSAR_LANCAMENTO",
                "cc-processar-lancamento"
            )

            self.queue = Queue(
                queue_name,
                connection=redis_conn
            )

            return

        # produção
        self.sqs = boto3.client(
            "sqs",
            region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        )

    def processar(self, event):
        with UnitOfWork() as uow:
            self.cliente = ClienteService(uow)
            self.lancamento_arquivo = LancamentoArquivoService(uow)
            self.lancamento = LancamentoService(uow)

            data_cad = now_sp_str()

            record = event["Records"][0]

            bucket = record["s3"]["bucket"]["name"]
            caminho_arquivo = unquote(
                record["s3"]["object"]["key"]
            )

            cliente_id, arquivo_parser_id, usuario_id = (
                self.extrair_ids_do_path_s3(caminho_arquivo)
            )

            nome_parser = self.cliente.get_parser(
                cliente_id,
                arquivo_parser_id
            )

            parser = ParserFactory.get_parser(
                nome_parser["nome_parser"]
            )

            response = self.s3.get_object(
                Bucket=bucket,
                Key=caminho_arquivo
            )

            arquivo_bytes = response["Body"].read()

            resultado = parser.parse(arquivo_bytes)

            lancamento_arquivo_id = (
                self.lancamento_arquivo.inserir(
                    cliente_id,
                    usuario_id,
                    caminho_arquivo,
                    data_cad
                )
            )

            print({
                "lancamento_arquivo_id": lancamento_arquivo_id
            })

            for payload_empresa in resultado:
                chave_agrupador = uuid.uuid4()

                lancamento_id = self.lancamento.inserir(
                    lancamento_arquivo_id,
                    payload_empresa,
                    chave_agrupador.hex,
                    data_cad
                )

                mensagem = {
                    "lancamento_arquivo_id": lancamento_arquivo_id,
                    "lancamento_id": lancamento_id
                }

                self.enviar_mensagem_fila(mensagem)

                print(mensagem)
                print("-" * 10)

        return {
            "statusCode": 200,
            "success": True,
        }

    def extrair_ids_do_path_s3(self, key: str):
        partes = key.split("/")

        try:
            cliente_id = int(partes[5])
            arquivo_parser_id = int(partes[6])
            usuario_id = int(partes[7])

        except (IndexError, ValueError):
            raise ValueError(
                f"Path S3 inválido: {key}"
            )

        return (
            cliente_id,
            arquivo_parser_id,
            usuario_id
        )

    def enviar_mensagem_fila(self, mensagem):

        # ambiente local → Redis/RQ
        if self.env == "local":

            # IMPORTANTE:
            # o worker RQ precisa consumir essa função
            #
            # rq worker cc-processar-lancamento --url redis://redis:6379
            #
            # e a função precisa existir:
            #
            # backend.app.jobs.processar_lancamento_job.processar_lancamento_job

            mensagem = self.formatar_mensagem_para_sqs(mensagem)
            self.queue.enqueue(
                processar_lancamento_job,
                mensagem
            )

            return

        # produção → AWS SQS
        queue_url = os.getenv("SQS_QUEUE_URL")

        if not queue_url:
            raise ValueError(
                "SQS_QUEUE_URL não configurada"
            )

        self.sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(mensagem),
            MessageAttributes={
                "source": {
                    "StringValue": (
                        "splitar-lancamento-service"
                    ),
                    "DataType": "String"
                }
            }
        )

    def formatar_mensagem_para_sqs(self, body):
        body = json.dumps(body)
        event = {'Records': [{
            'messageId': 'ea329e1f-2cd6-4a11-9f4d-eda0d40f658c',
            'receiptHandle': 'YzgwYzQ2ODEtNjEwYS00NTEwLTkyZDUtN2Q3NDg3OTdkODYyIGFybjphd3M6c3FzOnVzLWVhc3QtMTowMDAwMDAwMDAwMDA6Y2MtcHJvY2Vzc2FyLWxhbmNhbWVudG8gZWEzMjllMWYtMmNkNi00YTExLTlmNGQtZWRhMGQ0MGY2NThjIDE3NzQzMDgyOTcuOTI4NjA4Nw==',
            'body': body,
            'attributes': {
                'SenderId': '000000000000', 'SentTimestamp': '1774302329907',
                'AWSTraceHeader': 'Root=1-69c1b477-87ee26a9d1b0cda036bad172;Parent=0edea3b4decd506b;Sampled=1',
                'ApproximateReceiveCount': '167', 'ApproximateFirstReceiveTimestamp': '1774302332748'
            }, 'messageAttributes': {
                'source': {'stringValue': 'splitar-lancamento-service', 'dataType': 'String'}
            },
            'md5OfBody': '1ef4d694e05d47965a1ac5824e12053f',
            'md5OfMessageAttributes': '11b78e8aea91977248a255880905c9f3',
            'eventSourceARN': 'arn:aws:sqs:us-east-1:000000000000:cc-processar-lancamento',
            'eventSource': 'aws:sqs', 'awsRegion': 'us-east-1'
        }]}
        return event