from backend.app.core.database.base_repository import BaseRepository


class TipoUsuarioRepository(BaseRepository):

    def listar(self):

        query = "SELECT * FROM tipo_usuario"

        return self.fetch_all(query)