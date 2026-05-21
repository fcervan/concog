from backend.app.core.logging.loki_handler import setup_loki_logger

logger = setup_loki_logger("definir-status", extra_labels={"component": "service"})

class DefinirStatusLancamento:

    def definir(self, lancamento_agrupado):
        status_contagem = {'C': 0, 'P': 0, 'N': 0}

        for id_grupo, lancamentos in lancamento_agrupado.items():
            total_debito = 0
            total_credito = 0

            for lancamento in lancamentos:
                debito = float(lancamento.get('debito', 0))
                credito = float(lancamento.get('credito', 0))

                total_debito += debito
                total_credito += credito

            diferenca = round(total_credito - total_debito, 2)

            if diferenca == 0:
                status = 'C'
            elif -0.02 <= diferenca <= -0.01 or 0.01 <= diferenca <= 0.02:
                status = 'P'
            else:
                status = 'N'

            status_contagem[status] += 1

            lancamento_agrupado[id_grupo] = {
                'lancamentos': lancamentos,
                'status': status,
                'totais': {
                    'total_debito': round(total_debito, 2),
                    'total_credito': round(total_credito, 2),
                    'diferenca': diferenca
                }
            }

        logger.info(f"Status definidos - Conciliados: {status_contagem['C']}, Pendentes: {status_contagem['P']}, Nao conciliados: {status_contagem['N']}")

        return lancamento_agrupado