class ProcessarLancamentoService:

    def processar(self, event):
        print("Processando lançamentos...")
        return {
            "status": "ok",
            "acao": "processar_lancamento"
        }
