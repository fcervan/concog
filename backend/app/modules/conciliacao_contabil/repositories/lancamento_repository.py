from backend.app.core.database.base_repository import BaseRepository


class LancamentoRepository(BaseRepository):

    def listar_lancamento_sem_processamento_llm(self, lancamento_id):

        query = "select lancamento_dados from lancamento where lancamento_id = %s and data_atu_llm is null"

        return self.fetch_one(query, (lancamento_id))

    def inserir(self, lancamento_arquivo_id, lancamento_dados, chave_agrupador, data_cad):
        query = f"""
            INSERT INTO concog.lancamento (lancamento_arquivo_id, lancamento_dados, chave_agrupador, data_cad)
            VALUES (%s,%s,%s,%s);
        """
        return self.insert(query,(lancamento_arquivo_id, lancamento_dados, chave_agrupador, data_cad))
