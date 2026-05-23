import json
from backend.app.modules.conciliacao_contabil.repositories.lancamento_processado_repository import LancamentoProcessadoRepository
from backend.app.core.database.unit_of_work import UnitOfWork
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Tabela de Lançamentos</title>

    <!-- CSS Bootstrap via CDN -->
    <link 
        href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" 
        rel="stylesheet"
    >
</head>

<body class="bg-light">

<div class="container py-4">
    <h1 class="mb-4">Lançamentos Processados</h1>

    <table class="table table-bordered table-hover">
        <thead class="table-dark">
            <tr>
                <th>Histórico</th>
                <th>Débito</th>
                <th>Crédito</th>
                <th>Saldo</th>
                <th>ID Lançamento</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
            {linhas}
        </tbody>
    </table>
</div>

</body>
</html>
"""


def gerar_linhas(lanc):
    html = ""
    # print(lanc['saldo'])
    # print(lanc.get("status", ""))
    status = lanc.get("status", "")

    # Cores conforme status
    if status == "C":
        classe = "table-success"
    elif status == "N":
        classe = "table-danger"
    elif status == "P":
        classe = "table-warning"
    else:
        classe = "table-warning"
        status = "P"

    html += f"""
        <tr class="{classe}">
            <td>{lanc.get('historico', '')}</td>
            <td>{lanc.get('debito', '')}</td>
            <td>{lanc.get('credito', '')}</td>
            <td>{lanc.get('saldo', '')}</td>
            <td>{lanc.get('historico_id', '')}</td>
            <td>{status}</td>
        </tr>
    """

    return html
def lista_lancamento_id_processado():
    return [
        1,2,4,5,6,7,9,11,13,14,15,17,19,22,23,24,27,28,30,33,34,35,36,37,38,39,41,42,43,44,
        46,47,48,49,52,54,55,56,58,59,61,62,63,65,66,67,68,69,70,73,74,75,79,81,82,83,84,85,
        86,89,90,92,93,94,96,97,100,101,102,103,105,107,108,110,111,113,114,115
    ]
with UnitOfWork() as uow:
    lancamento_processado_repo = LancamentoProcessadoRepository(uow)

    for item_lancamento_id in lista_lancamento_id_processado():
        grupo_lancamentos = lancamento_processado_repo.listar_por_lancamento_arquivo_id_ordenado(2, item_lancamento_id)

        linhas_html = ''
        total_itens = len(grupo_lancamentos)

        for indice, lancamentos_processados in enumerate(grupo_lancamentos):
            lancamento_id = lancamentos_processados["lancamento_id"]

            proximo_lancamento_id = None
            if indice < total_itens - 1:
                proximo_lancamento_id = grupo_lancamentos[indice + 1]["lancamento_id"]

            if lancamento_id != proximo_lancamento_id:
                linhas_html += '<tr><td colspan="6"></td></tr>'
            for lancamento in json.loads(lancamentos_processados['lancamento_processado']):
                linhas = gerar_linhas(lancamento)
                linhas_html += linhas


        html_final = HTML_TEMPLATE.replace("{linhas}", linhas_html)

        with open(f"/home/fcervan/Downloads/lancamentos_id{lancamento_id}.html", "w", encoding="utf-8") as f:
            f.write(html_final)