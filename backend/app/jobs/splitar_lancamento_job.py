import sys
import os
# Adiciona a raiz do projeto ao path para imports funcionarem
# __file__ = backend/app/jobs/splitar_lancamento_job.py
# Precisamos subir 4 níveis para chegar em /home/fcervan/Documentos/concog
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from datetime import datetime

from backend.app.modules.conciliacao_contabil.services.splitar_lancamento_service import SplitarLancamentoService
from backend.app.utils.datetime_utils import diff_seconds

def processar_splitar(event):
    data_ini_processo = datetime.now()
    print(f"[{data_ini_processo.strftime('%Y-%m-%d %H:%M:%S')}] - [INFO] - WORKER - INICIO DO PROCESSO SPLITAR")

    service = SplitarLancamentoService()
    response = service.processar(event)

    data_fim_processo = datetime.now()
    tempo_processamento = diff_seconds(data_ini_processo, data_fim_processo)

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] - [INFO] - WORKER - FIM DO PROCESSO SPLITAR - PROCESSADO EM {tempo_processamento} SEGUNDOS")

    return response
