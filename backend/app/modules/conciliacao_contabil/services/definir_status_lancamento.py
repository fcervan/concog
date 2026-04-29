class DefinirStatusLancamento:

    def definir(self, lancamento_agrupado):
        # Itera sobre cada grupo de lançamentos
        for id_grupo, lancamentos in lancamento_agrupado.items():
            total_debito = 0
            total_credito = 0

            # Calcula o total de débitos e créditos do grupo
            for lancamento in lancamentos:
                # Converte os valores para float para fazer os cálculos
                debito = float(lancamento.get('debito', 0))
                credito = float(lancamento.get('credito', 0))

                total_debito += debito
                total_credito += credito

            # Calcula a diferença entre crédito e débito
            diferenca = round(total_credito - total_debito, 2)

            # Aplica as regras de negócio para definir o status
            if diferenca == 0:
                status = 'C'  # Conciliado
            elif -0.02 <= diferenca <= -0.01 or 0.01 <= diferenca <= 0.02:
                status = 'P'  # Pendente
            else:
                status = 'N'  # Não Conciliado

            # Adiciona o status ao grupo de lançamentos
            lancamento_agrupado[id_grupo] = {
                'lancamentos': lancamentos,
                'status': status,
                'totais': {
                    'total_debito': round(total_debito, 2),
                    'total_credito': round(total_credito, 2),
                    'diferenca': diferenca
                }
            }

        return lancamento_agrupado