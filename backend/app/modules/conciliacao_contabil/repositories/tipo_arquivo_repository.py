from backend.app.core.database.base_repository import BaseRepository


class TipoArquivoRepository(BaseRepository):

    def listar_todos(self):

        query = "SELECT * FROM tipo_arquivo"

        return self.fetch_all(query)