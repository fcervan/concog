from backend.app.core.database.base_repository import BaseRepository


class LancamentoRepository(BaseRepository):

    def listar_lancamentos_sem_processamento(self):

        query = """
            SELECT
                l.lancamento_dados, ta.classe_tipo_arquivo
                FROM lancamento l
                    inner join lancamento_arquivo la on l.lancamento_arquivo_id = la.lancamento_arquivo_id
                    inner join tipo_arquivo ta on la.tipo_arquivo_id = ta.tipo_arquivo_id
                    where l.agrupador_llm is null
        """

        return self.fetch_all(query)