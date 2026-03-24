from backend.app.modules.conciliacao_contabil.repositories.lancamento_repository import LancamentoRepository

class LancamentoService:

    def __init__(self, uow):
        self.repo = LancamentoRepository(uow)

    def listar_lancamento_sem_processamento_llm(self, lancamento_id):
        return self.repo.listar_lancamento_sem_processamento_llm(lancamento_id)

    def inserir(self, lancamento_arquivo_id, lancamento_dados, chave_agrupador, data_cad):
        return self.repo.inserir(lancamento_arquivo_id, lancamento_dados, chave_agrupador, data_cad)