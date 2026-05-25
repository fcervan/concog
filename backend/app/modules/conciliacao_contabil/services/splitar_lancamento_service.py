import json
import os
import uuid
from urllib.parse import unquote

import boto3
from redis import Redis
from rq import Queue

from backend.app.modules.conciliacao_contabil.parsers.parser_factory import ParserFactory
from backend.app.modules.conciliacao_contabil.repositories.cliente_repository import ClienteRepository
from backend.app.modules.conciliacao_contabil.repositories.lancamento_arquivo_repository import LancamentoArquivoRepository
from backend.app.modules.conciliacao_contabil.repositories.lancamento_repository import LancamentoRepository
from backend.app.core.database.unit_of_work import UnitOfWork
from backend.app.utils.datetime_utils import now_sp_str
from backend.app.jobs.processar_lancamento_job import processar_lancamento_job
from backend.app.core.logging.loki_handler import setup_loki_logger

logger = setup_loki_logger("splitar-lancamento-service", extra_labels={"component": "service"})


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

    def _validar_payload(self, payload: str, grupo_index: int):
        erros = []
        dados = json.loads(payload)
        lancamentos = dados.get("lancamentos", [])

        if not lancamentos:
            erros.append(
                f"Grupo {grupo_index + 1}: lista de lançamentos vazia"
            )
            return erros

        for i, lanc in enumerate(lancamentos):
            if "historico" not in lanc:
                erros.append(
                    f"Grupo {grupo_index + 1}, lançamento {i + 1}: campo 'historico' ausente. "
                    f"Chaves encontradas: {list(lanc.keys())}"
                )

        return erros

    def _validar_resultados(self, resultados):
        erros = []

        for i, payload in enumerate(resultados):
            erros.extend(self._validar_payload(payload, i))

        if erros:
            for erro in erros:
                log_data = json.dumps({
                    "evento": "validacao",
                    "status": "erro",
                    "cliente_id": self.cliente_id,
                    "arquivo": self.arquivo_nome,
                    "erro": erro
                })
                logger.error(log_data, extra={"loki_labels": {"cliente_id": str(self.cliente_id)}})
            raise ValueError("\n".join(erros))

    def processar(self, event):
        try:
            with UnitOfWork() as uow:
                self.cliente_repo = ClienteRepository(uow)
                self.lancamento_arquivo_repo = LancamentoArquivoRepository(uow)
                self.lancamento_repo = LancamentoRepository(uow)

                data_cad = now_sp_str()

                record = event["Records"][0]

                bucket = record["s3"]["bucket"]["name"]
                caminho_arquivo = unquote(
                    record["s3"]["object"]["key"]
                )

                self.cliente_id, arquivo_parser_id, usuario_id = (
                    self.extrair_ids_do_path_s3(caminho_arquivo)
                )

                self.arquivo_nome = caminho_arquivo.split("/")[-1]

                log_labels = {"loki_labels": {"cliente_id": str(self.cliente_id)}}

                log_data = json.dumps({
                    "evento": "inicio_processo",
                    "status": "processando",
                    "cliente_id": self.cliente_id,
                    "arquivo": self.arquivo_nome
                })
                logger.info(log_data, extra=log_labels)

                nome_parser = self.cliente_repo.get_parser(
                    self.cliente_id,
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

                if not resultado:
                    log_data = json.dumps({
                        "evento": "validacao",
                        "status": "erro",
                        "cliente_id": self.cliente_id,
                        "arquivo": self.arquivo_nome,
                        "erro": "Nenhum grupo de lançamentos foi encontrado no arquivo"
                    })
                    logger.error(log_data, extra=log_labels)
                    raise ValueError("Nenhum grupo de lançamentos foi encontrado no arquivo")

                self._validar_resultados(resultado)

                log_data = json.dumps({
                    "evento": "validacao",
                    "status": "sucesso",
                    "cliente_id": self.cliente_id,
                    "arquivo": self.arquivo_nome,
                    "grupos": len(resultado)
                })
                logger.info(log_data, extra=log_labels)

                lancamento_arquivo_id = (
                    self.lancamento_arquivo_repo.inserir(
                        self.cliente_id,
                        usuario_id,
                        caminho_arquivo,
                        data_cad
                    )
                )

                log_data = json.dumps({
                    "evento": "insert_arquivo",
                    "status": "sucesso",
                    "cliente_id": self.cliente_id,
                    "arquivo": self.arquivo_nome,
                    "lancamento_arquivo_id": lancamento_arquivo_id
                })
                logger.info(log_data, extra=log_labels)

                for payload_empresa in resultado:
                    chave_agrupador = uuid.uuid4()

                    lancamento_id = self.lancamento_repo.inserir(
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

                log_data = json.dumps({
                    "evento": "fim_processo",
                    "status": "sucesso",
                    "cliente_id": self.cliente_id,
                    "arquivo": self.arquivo_nome,
                    "grupos": len(resultado),
                    "lancamento_arquivo_id": lancamento_arquivo_id
                })
                logger.info(log_data, extra=log_labels)

            return {
                "statusCode": 200,
                "success": True,
            }

        except Exception as e:
            log_data = json.dumps({
                "evento": "erro_processo",
                "status": "erro",
                "cliente_id": getattr(self, "cliente_id", None),
                "arquivo": getattr(self, "arquivo_nome", None),
                "erro": str(e)
            })
            logger.error(log_data, extra={"loki_labels": {"cliente_id": str(getattr(self, "cliente_id", ""))}})
            raise

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