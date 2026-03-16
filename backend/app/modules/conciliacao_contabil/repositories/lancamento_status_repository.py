from backend.app.core.database.base_repository import BaseRepository


class LancamentoStatusRepository(BaseRepository):

    def listar(self):

        query = "SELECT * FROM lancamento_status"

        return self.fetch_all(query)