from backend.app.modules.conciliacao_contabil.services.processar_lancamento_service import ProcessarLancamentoService

def lambda_handler(event, context):
    # print(event)
    service = ProcessarLancamentoService()
    return service.classificar(event)

if __name__ == "__main__":
    event = {'Records': [{
        'messageId': 'ea329e1f-2cd6-4a11-9f4d-eda0d40f658c',
        'receiptHandle': 'YzgwYzQ2ODEtNjEwYS00NTEwLTkyZDUtN2Q3NDg3OTdkODYyIGFybjphd3M6c3FzOnVzLWVhc3QtMTowMDAwMDAwMDAwMDA6Y2MtcHJvY2Vzc2FyLWxhbmNhbWVudG8gZWEzMjllMWYtMmNkNi00YTExLTlmNGQtZWRhMGQ0MGY2NThjIDE3NzQzMDgyOTcuOTI4NjA4Nw==',
        'body': '{"lancamento_arquivo_id": 2, "lancamento_id": 2}',
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
    lambda_handler(event,'')

