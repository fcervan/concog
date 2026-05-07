from backend.app.modules.conciliacao_contabil.services.splitar_lancamento_service import SplitarLancamentoService
import os
def lambda_handler(event, context):
    # print(os.getenv("AWS_ENDPOINT_URL"))
    service = SplitarLancamentoService()
    return service.processar(event)

if __name__ == "__main__":
    event = {'Records': [
        {'eventVersion': '2.1', 'eventSource': 'aws:s3', 'awsRegion': 'us-east-1',
         'eventTime': '2026-03-17T03:42:39.910Z', 'eventName': 'ObjectCreated:Put', 'userIdentity':
             {'principalId': 'AIDAJDPLRKLG7UEXAMPLE'}, 'requestParameters': {'sourceIPAddress': '127.0.0.1'}, 'responseElements':
             {'x-amz-request-id': '96b9509a', 'x-amz-id-2': 'eftixk72aD6Ap51TnqcoF8eFidJG9Z/2'}, 's3':
             {'s3SchemaVersion': '1.0', 'configurationId': 'trigger-xlsx-arquivo-original', 'bucket':
                 {'name': 'concog', 'ownerIdentity': {'principalId': 'A3NL1KOZZKExample'}, 'arn': 'arn:aws:s3:::concog'}, 'object':
                 {'key': 'cc/arquivo-original/2026/03/16/1/1/1/base3k.xlsx', 'sequencer': '0055AED6DCD90281E5', 'eTag': '1f76dd5472649005af5d98155d47af09', 'size': 119473}}}]}
    lambda_handler(event,'')
