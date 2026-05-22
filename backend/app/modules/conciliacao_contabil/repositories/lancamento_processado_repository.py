from backend.app.core.database.base_repository import BaseRepository
from backend.app.core.logging.loki_handler import setup_loki_logger

logger = setup_loki_logger("lancamento-processado-repository", extra_labels={"component": "repository"})


class LancamentoProcessadoRepository(BaseRepository):

    def listar_por_lancamento_id(self, lancamento_id):
        logger.debug(f"Listando processados por lancamento_id: {lancamento_id}")
        query = "select * from lancamento_processado where lancamento_id = %s"
        return self.fetch_all(query, (lancamento_id))

    def listar_por_lancamento_arquivo_id(self, lancamento_arquivo_id):
        logger.debug(f"Listando processados por lancamento_arquivo_id: {lancamento_arquivo_id}")
        query = "select * from lancamento_processado where lancamento_arquivo_id = %s"
        return self.fetch_all(query, (lancamento_arquivo_id))

    def listar_por_lancamento_arquivo_id_ordenado(self, lancamento_arquivo_id, lancamento_id):
        logger.debug(f"Listando processados ordenados - arquivo: {lancamento_arquivo_id}, lancamento: {lancamento_id}")
        query = "select * from lancamento_processado where lancamento_arquivo_id = %s  and lancamento_id = %s order by lancamento_arquivo_id"
        return self.fetch_all(query, (lancamento_arquivo_id, lancamento_id))

    def inserir(self, lancamento_arquivo_id, lancamento_id, formato_usado, lancamento_processado, data_cad):
        logger.debug(f"Inserindo processado - arquivo: {lancamento_arquivo_id}, lancamento: {lancamento_id}")
        query = f"""
            INSERT INTO concog.lancamento_processado (lancamento_arquivo_id, lancamento_id, formato_usado, lancamento_processado, data_cad)
            VALUES (%s,%s,%s,%s,%s);
        """
        return self.insert(query,(lancamento_arquivo_id, lancamento_id, formato_usado, lancamento_processado, data_cad))

    def listar_vw_lancamento_processado_historico(self, historico_processado):
        logger.debug(f"Listando view historico: {historico_processado}")
        query = "select * from vw_lancamento_processado_historico where historico_processado = %s"
        return self.fetch_all(query, (historico_processado))
