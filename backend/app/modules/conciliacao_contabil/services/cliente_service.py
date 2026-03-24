from backend.app.modules.conciliacao_contabil.repositories.cliente_repository import ClienteRepository
class ClienteService:

    def __init__(self, uow):
        self.repo = ClienteRepository(uow)

    def get_parser(self, cliente_id, arquivo_parser_id):
        return self.repo.get_parser(cliente_id, arquivo_parser_id)

    def insert_cliente(self, nome):
        ...