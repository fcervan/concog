import json
from backend.app.modules.conciliacao_contabil.services.lancamento_processado_service import LancamentoProcessadoService
from backend.app.core.database.unit_of_work import UnitOfWork

def gerar_linhas(lanc):
    html = ""
    html += f"{lanc.get('historico_id', '')}"
    html += f";{lanc.get('historico', '')}"
    html += f";{lanc.get('debito', '')}"
    html += f";{lanc.get('credito', '')}"
    html += f";{lanc.get('saldo', '')}\n"

    return html
def lista_lancamento_id_processado():
    return [
        1,2,4,5,6,7,9,11,13,14,15,17,19,22,23,24,27,28,30,33,34,35,36,37,38,39,41,42,43,44,
        46,47,48,49,52,54,55,56,58,59,61,62,63,65,66,67,68,69,70,73,74,75,79,81,82,83,84,85,
        86,89,90,92,93,94,96,97,100,101,102,103,105,107,108,110,111,113,114,115
    ]

with (UnitOfWork() as uow):
    lancamento_processado = LancamentoProcessadoService(uow)

    for item_lancamento_id in lista_lancamento_id_processado():
        grupo_lancamentos = lancamento_processado.listar_por_lancamento_arquivo_id_ordenado(2, item_lancamento_id)

        linhas_html = ''
        total_itens = len(grupo_lancamentos)

        for indice, lancamentos_processados in enumerate(grupo_lancamentos):
            lancamento_id = lancamentos_processados["lancamento_id"]

            proximo_lancamento_id = None
            if indice < total_itens - 1:
                proximo_lancamento_id = grupo_lancamentos[indice + 1]["lancamento_id"]

            if lancamento_id != proximo_lancamento_id:
                linhas_html += "\n"
            for lancamento in json.loads(lancamentos_processados['lancamento_processado']):
                linhas = gerar_linhas(lancamento)
                linhas_html += linhas

        html_final = linhas_html

        with open(f"/home/fcervan/Downloads/dataset-csv/lancamentos_id{lancamento_id}.csv", "w", encoding="utf-8") as f:
            f.write(html_final)