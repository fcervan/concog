from backend.app.core.database.base_repository import BaseRepository


class ClienteRepository(BaseRepository):

    def get_parser(self, cliente_id, arquivo_parser_id):
        """
        Retorna o nome do Parser para ser usado
        :param cliente_id:
        :param arquivo_parser_id:
        :return:
        """
        query = """
            select
                ap.nome_parser
                from cliente c
                    inner join arquivo_parser_cliente apc on c.cliente_id = apc.cliente_id
                    inner join arquivo_parser ap on apc.arquivo_parser_id = ap.arquivo_parser_id
                where
                    apc.cliente_id = 1 and apc.arquivo_parser_id = 1
        """

        return self.fetch_one(query)