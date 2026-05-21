from backend.app.modules.conciliacao_contabil.repositories.lancamento_processado_llm_repository import LancamentoProcessadoLlmRepository
from backend.app.core.logging.loki_handler import setup_loki_logger

logger = setup_loki_logger("lancamento-processado-llm", extra_labels={"component": "service"})

class LancamentoProcessadoLlmService:

    def __init__(self, uow):
        self.repo = LancamentoProcessadoLlmRepository(uow)

    def listar_por_lancamento_id(self, lancamento_id):
        logger.debug(f"Listando processados por lancamento_id: {lancamento_id}")
        return self.repo.listar_por_lancamento_id(lancamento_id)

    def listar_por_lancamento_arquivo_id(self, lancamento_arquivo_id):
        logger.debug(f"Listando processados por lancamento_arquivo_id: {lancamento_arquivo_id}")
        return self.repo.listar_por_lancamento_arquivo_id(lancamento_arquivo_id)

    def listar_por_lancamento_arquivo_id_ordenado(self, lancamento_arquivo_id, lancamento_id):
        logger.debug(f"Listando processados ordenados - arquivo: {lancamento_arquivo_id}, lancamento: {lancamento_id}")
        return self.repo.listar_por_lancamento_arquivo_id_ordenado(lancamento_arquivo_id, lancamento_id)

    def inserir(self, lancamento_arquivo_id, lancamento_id, llm_usado, lancamento_processado, data_cad):
        logger.info(f"Inserindo processado - arquivo: {lancamento_arquivo_id}, lancamento: {lancamento_id}, llm: {llm_usado}")
        return self.repo.inserir(lancamento_arquivo_id, lancamento_id, llm_usado, lancamento_processado, data_cad)

    def listar_vw_lancamento_processado_historico(self, historico_processado):
        logger.debug(f"Listando view historico: {historico_processado}")
        return self.repo.listar_vw_lancamento_processado_historico(historico_processado)

    def finalizar_processamento(self):
        logger.info("Finalizando processamento")
        ...