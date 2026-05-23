from backend.app.modules.conciliacao_contabil.repositories.lancamento_repository import LancamentoRepository
from backend.app.modules.conciliacao_contabil.repositories.lancamento_processado_repository import LancamentoProcessadoRepository
from backend.app.core.database.unit_of_work import UnitOfWork
from datetime import datetime
import time
import json

def lambda_handler(event, context):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] - [INFO] - INICIO DO PROCESSO")
    # service = ProcessarLancamentoService()
    # return service.classificar(event)

def mensagem_sqs(lancamento_id):
    return {'Records': [{
        'messageId': 'ea329e1f-2cd6-4a11-9f4d-eda0d40f658c',
        'receiptHandle': 'YzgwYzQ2ODEtNjEwYS00NTEwLTkyZDUtN2Q3NDg3OTdkODYyIGFybjphd3M6c3FzOnVzLWVhc3QtMTowMDAwMDAwMDAwMDA6Y2MtcHJvY2Vzc2FyLWxhbmNhbWVudG8gZWEzMjllMWYtMmNkNi00YTExLTlmNGQtZWRhMGQ0MGY2NThjIDE3NzQzMDgyOTcuOTI4NjA4Nw==',
        'body': '{"lancamento_id": '+str(lancamento_id)+', "lancamento_arquivo_id": 2}',
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

if __name__ == "__main__":
    with UnitOfWork() as uow:
        lancamento_processado_repo = LancamentoProcessadoRepository(uow)
        lancamento_repo = LancamentoRepository(uow)

        # for lancamento_id in range(1,323):
        for lancamento_id in range(1,116):
            lancamento_dados = lancamento_repo.listar_lancamento_sem_processamento(lancamento_id)
            lancamentos = json.loads(lancamento_dados["lancamento_dados"])

            total_lancamentos = len(lancamentos["lancamentos"])
            total_lancamentos_processados = 0


            for lancamento in lancamentos["lancamentos"]:
                lancamento_processado = lancamento_processado_repo.listar_vw_lancamento_processado_historico(
                    lancamento["historico"]
                )
                if lancamento_processado:
                    total_lancamentos_processados += 1
            if total_lancamentos == total_lancamentos_processados:
                print(lancamento_dados)
                exit()
                print(f"[SUCESSO] - Lancamento_arquivo_id {lancamento['lancamento_arquivo_id']} pronto para gerar dataset")
                continue
            # print(f"[ERRO] - Lancamento_id {lancamento_id} inconsistente: lancamento {total_lancamentos} - lancamento_processado: {total_lancamentos_processados}")
            # event = mensagem_sqs(lancamento_id)
            # lambda_handler(event,'')
            # print("_"*10)
            # time.sleep(4)


