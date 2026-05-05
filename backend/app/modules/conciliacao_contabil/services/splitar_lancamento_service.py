import json

import boto3
import os
from urllib.parse import unquote
import uuid

from backend.app.modules.conciliacao_contabil.parsers.parser_factory import ParserFactory
from backend.app.modules.conciliacao_contabil.services.cliente_service import ClienteService
from backend.app.modules.conciliacao_contabil.services.lancamento_arquivo_service import LancamentoArquivoService
from backend.app.modules.conciliacao_contabil.services.lancamento_service import LancamentoService
from backend.app.core.database.unit_of_work import UnitOfWork
from backend.app.utils.datetime_utils import now_sp_str


class SplitarLancamentoService:

    def __init__(self):
        self.cliente = None

        self.s3 = boto3.client(
            "s3",
            endpoint_url=os.getenv("AWS_ENDPOINT_URL")
        )

        self.sqs = boto3.client(
            "sqs",
            endpoint_url=os.getenv("AWS_ENDPOINT_URL")  # importante pro LocalStack
        )

    def processar(self, event):
        with UnitOfWork() as uow:
            self.cliente = ClienteService(uow)
            self.lancamento_arquivo = LancamentoArquivoService(uow)
            self.lancamento = LancamentoService(uow)

            data_cad = now_sp_str()

            record = event["Records"][0]

            bucket = record["s3"]["bucket"]["name"]
            caminho_arquivo = unquote(record["s3"]["object"]["key"])

            cliente_id, arquivo_parser_id, usuario_id = self.extrair_ids_do_path_s3(caminho_arquivo)

            # print([cliente_id, arquivo_parser_id, usuario_id])
            nome_parser = self.cliente.get_parser(cliente_id, arquivo_parser_id)

            parser = ParserFactory.get_parser(nome_parser['nome_parser'])

            response = self.s3.get_object(Bucket=bucket, Key=caminho_arquivo)
            arquivo_bytes = response["Body"].read()

            resultado = parser.parse(arquivo_bytes)

            lancamento_arquivo_id = self.lancamento_arquivo.inserir(
                cliente_id,
                usuario_id,
                caminho_arquivo,
                data_cad
            )

            print({"lancamento_arquivo_id": lancamento_arquivo_id})

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
                self.enviar_mensagem_sqs(mensagem)
                print(os.getenv("SQS_CC_PROCESSAR_LANCAMENTO"))
                print(payload_empresa)
                print("-"*10)

        return {
            'statusCode': 200,
            'success': True,
        }

    def extrair_ids_do_path_s3(self, key: str):
        partes = key.split("/")
        try:
            cliente_id = int(partes[5])
            arquivo_parser_id = int(partes[6])
            usuario_id = int(partes[7])
        except (IndexError, ValueError):
            raise ValueError(f"Path S3 inválido: {key}")

        return cliente_id, arquivo_parser_id, usuario_id

    def enviar_mensagem_sqs(self, mensagem):
        queue_name = os.getenv("SQS_CC_PROCESSAR_LANCAMENTO", 'cc-processar-lancamento')

        if not queue_name:
            raise ValueError("Variável de ambiente SQS_CC_PROCESSAR_LANCAMENTO não definida")

        # Recupera a URL da fila pelo nome
        response = self.sqs.get_queue_url(QueueName=queue_name)
        queue_url = response["QueueUrl"]

        # Envia a mensagem
        self.sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(mensagem),
            # opcional (bom pra debug e rastreio)
            MessageAttributes={
                "source": {
                    "StringValue": "splitar-lancamento-service",
                    "DataType": "String"
                }
            }
        )