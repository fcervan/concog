import json
from datetime import datetime

from backend.app.modules.conciliacao_contabil.services.agrupar_lancamento_service import AgruparLancamentoService
from backend.app.modules.conciliacao_contabil.services.definir_status_lancamento import DefinirStatusLancamento
from backend.app.modules.conciliacao_contabil.repositories.lancamento_repository import LancamentoRepository
from backend.app.modules.conciliacao_contabil.services.lancamento_processado_service import LancamentoProcessadoService
from backend.app.core.database.unit_of_work import UnitOfWork
from backend.app.core.logging.loki_handler import setup_loki_logger

logger = setup_loki_logger("classificar-lancamento", extra_labels={"component": "service"})


class ClassificarLancamentoService:

    def __init__(self):
        self.agrupar_lancamento_service = AgruparLancamentoService()
        self.definir_status_lancamento = DefinirStatusLancamento()

    def classificar(self, event):

        for mensagem in event["Records"]:
            try:
                with UnitOfWork() as uow:
                    lancamento_repository = LancamentoRepository(uow)
                    lancamento_processado_service = LancamentoProcessadoService(uow)

                    mensagem_lancamento = json.loads(mensagem['body'])
                    logger.info(f"Mensagem recebida - lancamento_id: {mensagem_lancamento['lancamento_id']}")

                    lancamentos = lancamento_repository.listar_lancamento_sem_processamento(
                        mensagem_lancamento['lancamento_id']
                    )

                    logger.debug(f"Lancamentos recuperados do banco para lancamento_id: {mensagem_lancamento['lancamento_id']}")

                    lancamento_agrupado = self.agrupar_lancamento_service.agrupar(
                        lancamentos["lancamento_dados"]
                    )

                    logger.debug(f"Lancamentos agrupados em {len(lancamento_agrupado)} grupos")

                    lancamento_definido = self.definir_status_lancamento.definir(
                        lancamento_agrupado
                    )

                    logger.info(f"Status definido para {len(lancamento_definido)} grupos")

                    data_cad = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    lancamento_processado_service.inserir(
                        mensagem_lancamento['lancamento_arquivo_id'],
                        mensagem_lancamento['lancamento_id'],
                        'spacy',
                        json.dumps(lancamento_definido),
                        data_cad
                    )

                    lancamento_repository.atualizar_data_llm(mensagem_lancamento['lancamento_id'], data_cad)

                    logger.info(f"Lancamento {mensagem_lancamento['lancamento_id']} processado e salvo com sucesso")

            except Exception as e:
                logger.error(f"Erro ao processar mensagem: {e}", exc_info=True)

        return {'statusCode': 200, 'success': True}