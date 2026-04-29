import json
from datetime import datetime

from backend.app.modules.conciliacao_contabil.services.agrupar_lancamento_service import AgruparLancamentoService
from backend.app.modules.conciliacao_contabil.services.definir_status_lancamento import DefinirStatusLancamento
from backend.app.modules.conciliacao_contabil.repositories.lancamento_repository import LancamentoRepository
from backend.app.modules.conciliacao_contabil.services.lancamento_processado_llm_service import LancamentoProcessadoLlmService
from backend.app.core.database.unit_of_work import UnitOfWork


class ClassificarLancamentoService:

    def __init__(self):
        self.agrupar_lancamento_service = AgruparLancamentoService()
        self.definir_status_lancamento = DefinirStatusLancamento()

    def classificar(self, event):

        for mensagem in event["Records"]:
            try:
                with UnitOfWork() as uow:
                    lancamento_repository = LancamentoRepository(uow)
                    lancamento_processamento_llm_service = LancamentoProcessadoLlmService(uow)

                    mensagem_lancamento = json.loads(mensagem['body'])
                    print("Mensagem recebida:", mensagem_lancamento)

                    lancamentos = lancamento_repository.listar_lancamento_sem_processamento(
                        mensagem_lancamento['lancamento_id']
                    )

                    lancamento_agrupado = self.agrupar_lancamento_service.agrupar(
                        lancamentos["lancamento_dados"]
                    )

                    lancamento_definido = self.definir_status_lancamento.definir(
                        lancamento_agrupado
                    )

                    print(json.dumps(lancamento_definido, indent=4))

                    data_cad = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    lancamento_processamento_llm_service.inserir(
                        mensagem_lancamento['lancamento_arquivo_id'],
                        mensagem_lancamento['lancamento_id'],
                        'spacy',
                        json.dumps(lancamento_definido),
                        data_cad
                    )

                    lancamento_repository.atualizar_data_llm(mensagem_lancamento['lancamento_id'], data_cad)

            except Exception as e:
                print(f"Erro ao processar mensagem {mensagem}: {e}")
                # aqui você pode:
                # - logar
                # - mandar pra DLQ
                # - ou só seguir

        return {'statusCode': 200, 'success': True}