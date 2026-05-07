from datetime import datetime

from backend.app.modules.conciliacao_contabil.services.classificar_lancamento_service import ClassificarLancamentoService
from backend.app.utils.datetime_utils import diff_seconds

def processar_lancamento_job(event):
    data_ini_processo = datetime.now()
    print(f"[{data_ini_processo.strftime('%Y-%m-%d %H:%M:%S')}] - [INFO] - WORKER - INICIO DO PROCESSO")

    service = ClassificarLancamentoService()
    response = service.classificar(event)

    data_fim_processo = datetime.now()
    tempo_processamento = diff_seconds(data_ini_processo, data_fim_processo)

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] - [INFO] - WORKER - FIM DO PROCESSO - PROCESSADO EM {tempo_processamento} SEGUNDOS")

    return response