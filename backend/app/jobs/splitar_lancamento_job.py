import sys
import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from datetime import datetime

from backend.app.modules.conciliacao_contabil.services.splitar_lancamento_service import SplitarLancamentoService
from backend.app.utils.datetime_utils import diff_seconds
from backend.app.core.logging.loki_handler import setup_loki_logger

logger = setup_loki_logger("splitar-lancamento", extra_labels={"component": "worker"})

def processar_splitar(event):
    data_ini_processo = datetime.now()
    logger.info("INICIO DO PROCESSO SPLITAR")

    service = SplitarLancamentoService()
    response = service.processar(event)

    data_fim_processo = datetime.now()
    tempo_processamento = diff_seconds(data_ini_processo, data_fim_processo)

    logger.info(f"FIM DO PROCESSO SPLITAR - PROCESSADO EM {tempo_processamento} SEGUNDOS")

    return response
