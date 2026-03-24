from backend.app.modules.conciliacao_contabil.repositories.lancamento_arquivo_repository import LancamentoArquivoRepository

class LancamentoArquivoService:

    def __init__(self, uow):
        self.repo = LancamentoArquivoRepository(uow)

    def inserir(self, cliente_id, usuario_id, s3_path, data_cad):
        return self.repo.inserir(cliente_id, usuario_id, s3_path, data_cad)