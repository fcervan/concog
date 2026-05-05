from backend.app.core.database.base_repository import BaseRepository


class LancamentoProcessadoLlmRepository(BaseRepository):

    def listar_por_lancamento_id(self, lancamento_id):

        query = "select * from lancamento_processado_llm where lancamento_id = %s"

        return self.fetch_all(query, (lancamento_id))

    def listar_por_lancamento_arquivo_id(self, lancamento_arquivo_id):

        query = "select * from lancamento_processado_llm where lancamento_arquivo_id = %s"

        return self.fetch_all(query, (lancamento_arquivo_id))

    def listar_por_lancamento_arquivo_id_ordenado(self, lancamento_arquivo_id, lancamento_id):

        query = "select * from lancamento_processado_llm where lancamento_arquivo_id = %s  and lancamento_id = %s order by lancamento_arquivo_id"

        return self.fetch_all(query, (lancamento_arquivo_id, lancamento_id))

    def inserir(self, lancamento_arquivo_id, lancamento_id, llm_usado, lancamento_processado, data_cad):
        query = f"""
            INSERT INTO concog.lancamento_processado_llm (lancamento_arquivo_id, lancamento_id, llm_usado, lancamento_processado, data_cad)
            VALUES (%s,%s,%s,%s,%s);
        """

        return self.insert(query,(lancamento_arquivo_id, lancamento_id, llm_usado, lancamento_processado, data_cad))

    def listar_vw_lancamento_processado_historico(self, historico_processado):

        query = "select * from vw_lancamento_processado_historico where historico_processado = %s"

        return self.fetch_all(query, (historico_processado))
