import json
import csv
from io import StringIO

from backend.app.core.ai.llm.llm_factory import get_llm
from backend.app.core.ai.prompts.prompt_loader import load_prompt
from backend.app.modules.conciliacao_contabil.repositories.lancamento_repository import LancamentoRepository


"""
Para testar no terminal:
python -m backend.app.modules.conciliacao_contabil.services.processar_lancamento_service
"""
class ProcessarLancamentoService:

    def __init__(self):
        self.llm = get_llm()

        self.system_prompt = load_prompt(
            "conciliacao_contabil/cc_processar_lancamento/classificar_lancamento_system.txt"
        )
        self.lancamento = LancamentoRepository()

    def classificar(self, event):

        lancamentos = self.lancamento.listar_lancamentos_sem_processamento()

        colunas = ["HISTORICO", "DEBITO", "CREDITO", "SALDO", "LANCAMENTO_ID"]

        buffer = StringIO()

        writer = csv.DictWriter(
            buffer,
            fieldnames=colunas,
            delimiter=";",
            quoting=csv.QUOTE_MINIMAL
        )

        # header
        writer.writeheader()

        for lancamento in lancamentos:
            lancamento_dados = json.loads(lancamento["lancamento_dados"])

            linha = {col: lancamento_dados.get(col, "") for col in colunas}

            writer.writerow(linha)

        tabela_lancamentos = buffer.getvalue()

        print("Tabela gerada:")
        print(tabela_lancamentos)

        resposta = self.llm.generate(
            system_prompt=self.system_prompt,
            user_prompt=tabela_lancamentos
        )

        print(resposta)

        return resposta


if __name__ == "__main__":
    service = ProcessarLancamentoService()
    service.classificar({})