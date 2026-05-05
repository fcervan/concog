import json
import csv
from io import StringIO
from datetime import datetime

from backend.app.core.ai.llm.llm_factory import get_llm
from backend.app.core.ai.prompts.prompt_loader import load_prompt
from backend.app.modules.conciliacao_contabil.services.lancamento_service import LancamentoService
from backend.app.modules.conciliacao_contabil.services.lancamento_processado_llm_service import LancamentoProcessadoLlmService
from backend.app.core.database.unit_of_work import UnitOfWork
from backend.app.utils.datetime_utils import now_sp_str, diff_seconds
from backend.app.core.config.settings import LLM_PROVIDER, GROQ_MODEL


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
        try:
            with UnitOfWork() as uow:
                self.lancamento = LancamentoService(uow)
                self.lancamento_processado_llm = LancamentoProcessadoLlmService(uow)
                for mensagem in event["Records"]:
                    data_cad = now_sp_str()

                    # Mensagem da fila
                    mensagem_lancamento = json.loads(mensagem['body'])
                    print("Mensagem recebida:", mensagem_lancamento)

                    # Obtém o JSON do banco
                    lancamento = self.lancamento.listar_lancamento_sem_processamento_llm(
                        mensagem_lancamento['lancamento_id']
                    )

                    # Lê o JSON vindo do banco
                    dados = json.loads(lancamento["lancamento_dados"])
                    lancamentos = dados.get("lancamentos", [])

                    # Campos do CSV
                    colunas = ["HISTORICO", "DEBITO", "CREDITO", "SALDO", "HISTORICO_ID"]
                    colunas_llm = ["HISTORICO", "HISTORICO_ID"]

                    # Criar buffer para gerar CSV em memória
                    buffer = StringIO()
                    buffer_llm = StringIO()

                    writer = csv.DictWriter(
                        buffer,
                        fieldnames=colunas,
                        delimiter=";",
                        quoting=csv.QUOTE_MINIMAL
                    )

                    writer_llm = csv.DictWriter(
                        buffer_llm,
                        fieldnames=colunas_llm,
                        delimiter=";",
                        quoting=csv.QUOTE_MINIMAL
                    )

                    writer.writeheader()
                    writer_llm.writeheader()

                    # Preenche todas as linhas
                    for i, item in enumerate(lancamentos, start=1):
                        linha = {
                            "HISTORICO": item.get("historico", ""),
                            "DEBITO": item.get("debito", ""),
                            "CREDITO": item.get("credito", ""),
                            "SALDO": item.get("saldo", ""),
                            "HISTORICO_ID": i
                        }
                        writer.writerow(linha)

                        linha_llm = {
                            "HISTORICO": item.get("historico", ""),
                            "HISTORICO_ID": i
                        }
                        writer_llm.writerow(linha_llm)

                    tabela_lancamentos = buffer.getvalue()
                    tabela_lancamentos_llm = buffer_llm.getvalue()

                    # print("CSV gerado:")
                    print(tabela_lancamentos)
                    print(tabela_lancamentos_llm)
                    # print("==== FIM ====")
                    # return {
                    #     'statusCode': 200,
                    #     'success': True,
                    # }

                    data_ini_processo = datetime.now()
                    print(f"[{data_ini_processo.strftime('%Y-%m-%d %H:%M:%S')}] - [INFO] - PROCESSANDO INFERENCIA VIA {LLM_PROVIDER}/{GROQ_MODEL}")
                    # Enviar CSV para o LLM
                    resposta = self.llm.generate(
                        system_prompt=self.system_prompt,
                        user_prompt=tabela_lancamentos_llm
                    )
                    data_fim_processo = datetime.now()
                    tempo_processamento = diff_seconds(data_ini_processo, data_fim_processo)
                    print(f"[{data_fim_processo.strftime('%Y-%m-%d %H:%M:%S')}] - [INFO] - INFERENCIA FINALIZADA VIA {LLM_PROVIDER}/{GROQ_MODEL} - PROCESSADO EM {tempo_processamento} SEGUNDOS")

                    print("Resposta LLM:")
                    print(resposta)
                    print('')
                    classificados = self.gerar_json_lancamentos(resposta, lancamentos)
                    # print(json.dumps(classificados))
                    # return {
                    #     'statusCode': 200,
                    #     'success': True,
                    # }
                    for classificado in classificados['grupos']:
                        self.lancamento_processado_llm.inserir(
                            mensagem_lancamento['lancamento_arquivo_id'],
                            mensagem_lancamento['lancamento_id'],
                            LLM_PROVIDER,
                            json.dumps(classificado),
                            data_cad
                        )
                        # print(json.dumps(classificado))
                        # print('')
        except Exception as e:
            print(f"ERRO AO CLASSIFICAR: {e}")
            print(f"LANCAMENTO_ID: {mensagem_lancamento['lancamento_id']}")
            print("="*50)

        return {
            'statusCode': 200,
            'success': True,
        }

    def gerar_json_lancamentos(self, texto: str, dados_originais: list):
        """
        texto: retorno do LLM no formato:
            HISTORICO;HISTORICO_ID
            ...
            ---
            ...
        dados_originais: lista original de lançamentos contendo DEBITO, CREDITO e SALDO.
                         Ex: [{"historico": "...", "debito": "...", "credito": "...", "saldo": "..."}]
        """
        # Criar mapa para recuperar valores originais usando HISTORICO_ID
        mapa_original = {}
        for idx, item in enumerate(dados_originais, start=1):
            mapa_original[idx] = {
                "debito": item.get("debito", ""),
                "credito": item.get("credito", ""),
                "saldo": item.get("saldo", "")
            }

        grupos_brutos = texto.strip().split("---")
        resultado = []

        for grupo in grupos_brutos:
            grupo = grupo.strip()
            if not grupo:
                continue

            linhas = grupo.split("\n")
            lancamento_final = []

            for linha in linhas:
                partes = linha.split(";")
                if len(partes) != 2:
                    raise ValueError(f"Linha inválida: {linha}")

                historico, historico_id = partes
                historico_id = int(historico_id)

                # Recuperar dados originais
                dados_recuperados = mapa_original.get(historico_id, {
                    "debito": "",
                    "credito": "",
                    "saldo": ""
                })

                # Construir linha final corrigida
                lancamento_final.append({
                    "historico": historico.strip(),
                    "historico_id": historico_id,
                    "debito": dados_recuperados["debito"],
                    "credito": dados_recuperados["credito"],
                    "saldo": dados_recuperados["saldo"],
                })

            resultado.append(lancamento_final)

        return {"grupos": resultado}
