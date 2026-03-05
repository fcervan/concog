class SplitarLancamentoService:

    def processar(self, event):
        print("Splitando lançamentos...")
        return {
            "status": "ok",
            "acao": "splitar_lancamento"
        }
