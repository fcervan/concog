import json
import csv
from io import StringIO

from backend.app.core.ai.llm.llm_factory import get_llm
from backend.app.core.ai.prompts.prompt_loader import load_prompt
from backend.app.modules.conciliacao_contabil.services.lancamento_service import LancamentoService
from backend.app.core.database.unit_of_work import UnitOfWork


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

    def classificar(self, event):
        with UnitOfWork() as uow:
            for mensagem in event["Records"]:

                # Mensagem da fila
                mensagem_lancamento = json.loads(mensagem['body'])
                print("Mensagem recebida:", mensagem_lancamento)

                self.lancamento = LancamentoService(uow)

                # Obtém o JSON do banco
                lancamento = self.lancamento.listar_lancamento_sem_processamento_llm(
                    mensagem_lancamento['lancamento_id']
                )

                # Lê o JSON vindo do banco
                dados = json.loads(lancamento["lancamento_dados"])
                lancamentos = dados.get("lancamentos", [])

                # Campos do CSV
                colunas = ["HISTORICO", "DEBITO", "CREDITO", "SALDO", "LANCAMENTO_ID"]

                # Criar buffer para gerar CSV em memória
                buffer = StringIO()

                writer = csv.DictWriter(
                    buffer,
                    fieldnames=colunas,
                    delimiter=";",
                    quoting=csv.QUOTE_MINIMAL
                )

                writer.writeheader()

                # Preenche todas as linhas
                for i, item in enumerate(lancamentos, start=1):
                    linha = {
                        "HISTORICO": item.get("historico", ""),
                        "DEBITO": item.get("debito", ""),
                        "CREDITO": item.get("credito", ""),
                        "SALDO": item.get("saldo", ""),
                        "LANCAMENTO_ID": i
                    }
                    writer.writerow(linha)

                tabela_lancamentos = buffer.getvalue()

                print("CSV gerado:")
                print(tabela_lancamentos)
                # print("==== FIM ====")
                # exit()

                # Enviar CSV para o LLM
                resposta = self.llm.generate(
                    system_prompt=self.system_prompt,
                    user_prompt=tabela_lancamentos
                )

                print("Resposta LLM:")
                print(resposta)

        return {
            'statusCode': 200,
            'success': True,
        }

