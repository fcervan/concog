import boto3
import os
from urllib.parse import unquote

from backend.app.modules.conciliacao_contabil.parsers.parser_factory import ParserFactory
from backend.app.modules.conciliacao_contabil.repositories.cliente_repository import ClienteRepository


class SplitarLancamentoService:

    def __init__(self):
        self.cliente = ClienteRepository()
        self.s3 = boto3.client(
            "s3",
            endpoint_url=os.getenv("AWS_ENDPOINT_URL")
        )

    def processar(self, event):

        record = event["Records"][0]

        bucket = record["s3"]["bucket"]["name"]
        caminho_arquivo = unquote(record["s3"]["object"]["key"])

        cliente_id, arquivo_parser_id = self.extrair_ids_do_path_s3(caminho_arquivo)
        # print(os.getenv("AWS_ENDPOINT_URL"))
        # print([cliente_id, arquivo_parser_id])
        nome_parser = self.cliente.get_parser(cliente_id, arquivo_parser_id)

        parser = ParserFactory.get_parser(nome_parser['nome_parser'])

        response = self.s3.get_object(Bucket=bucket, Key=caminho_arquivo)
        arquivo_bytes = response["Body"].read()

        resultado = parser.parse(arquivo_bytes)

        for payload_empresa in resultado:
            caminho_arquivo_json = "cc/..."
            self.salvar_arquivo_s3(caminho_arquivo_json)
            self.enviar_mensagem_sqs(caminho_arquivo_json, cliente_id, arquivo_parser_id)
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
        except (IndexError, ValueError):
            raise ValueError(f"Path S3 inválido: {key}")

        return cliente_id, arquivo_parser_id

    def salvar_arquivo_s3(self, caminho_arquivo):
        ...

    def enviar_mensagem_sqs(self, caminho_arquivo_json, cliente_id, arquivo_parser_id):
        ...