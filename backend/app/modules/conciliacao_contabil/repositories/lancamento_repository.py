from backend.app.core.database.base_repository import BaseRepository
from backend.app.core.logging.loki_handler import setup_loki_logger

logger = setup_loki_logger("lancamento-repository", extra_labels={"component": "repository"})


class LancamentoRepository(BaseRepository):

    def listar_lancamento_sem_processamento(self, lancamento_id):
        logger.debug(f"Buscando lancamento sem processamento - id: {lancamento_id}")
        query = "select * from lancamento where lancamento_id = %s and data_atu_llm is null"
        return self.fetch_one(query, (lancamento_id))

    def inserir(self, lancamento_arquivo_id, lancamento_dados, chave_agrupador, data_cad):
        logger.debug(f"Inserindo lancamento - arquivo: {lancamento_arquivo_id}")
        query = f"""
            INSERT INTO concog.lancamento (lancamento_arquivo_id, lancamento_dados, chave_agrupador, data_cad)
            VALUES (%s,%s,%s,%s);
        """
        return self.insert(query,(lancamento_arquivo_id, lancamento_dados, chave_agrupador, data_cad))

    def atualizar_data_llm(self, lancamento_id, data_atu_llm):
        logger.debug(f"Atualizando data_llm - lancamento: {lancamento_id}")
        query = f"""
            UPDATE concog.lancamento SET data_atu_llm = %s WHERE lancamento_id = %s
        """
        return self.insert(query,(data_atu_llm, lancamento_id))
