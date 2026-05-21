from datetime import datetime

from backend.app.modules.conciliacao_contabil.services.classificar_lancamento_service import ClassificarLancamentoService
from backend.app.utils.datetime_utils import diff_seconds
from backend.app.core.logging.loki_handler import setup_loki_logger

logger = setup_loki_logger("processar-lancamento", extra_labels={"component": "worker"})

def processar_lancamento_job(event):
    data_ini_processo = datetime.now()
    logger.info("INICIO DO PROCESSO")

    service = ClassificarLancamentoService()
    response = service.classificar(event)

    data_fim_processo = datetime.now()
    tempo_processamento = diff_seconds(data_ini_processo, data_fim_processo)

    logger.info(f"FIM DO PROCESSO - PROCESSADO EM {tempo_processamento} SEGUNDOS")

    return response