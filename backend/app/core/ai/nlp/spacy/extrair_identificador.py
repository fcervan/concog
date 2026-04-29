import spacy
from datetime import datetime
from backend.app.utils.datetime_utils import diff_seconds

data_ini_processo = datetime.now()
print(f"[{data_ini_processo.strftime('%Y-%m-%d %H:%M:%S')}] - [INFO] - CARREGANDO MODELO SPACY")

nlp = spacy.load("backend/app/core/ai/nlp/spacy/modelo_spacy")

def extrair(texto):

    doc = nlp(texto)

    ids = [ent.text for ent in doc.ents if ent.label_ == "IDENTIFICADOR"]

    return ids


if __name__ == "__main__":
    textos = [
        "COMPRA DE MERCADORIAS 2364  2 31/01/2025 ROCAMI PARAFUSOS E FERRAGENS EIRELI EPP",
        "NF 2364 ROCAMI PARAFUSOS E FERRAGENS EIRELI EPP PARAFUSO",
        "COMPRA DE MERCADORIAS 2400  2 31/03/2025 ROCAMI PARAFUSOS E FERRAGENS EIRELI EPP",
    ]


    data_fim_processo = datetime.now()
    tempo_processamento = diff_seconds(data_ini_processo, data_fim_processo)
    print(f"[{data_fim_processo.strftime('%Y-%m-%d %H:%M:%S')}] - [INFO] - MODELO CARREGADO EM {tempo_processamento} SEGUNDOS")
    print(f"[{data_fim_processo.strftime('%Y-%m-%d %H:%M:%S')}] - [INFO] - INICIANDO PROCESSAMENTO")
    for t in textos:
        ids = extrair(t)

        try:
            print(f"✔️ - Identificador encontrado com sucesso: {ids[0]} -> {t}")
            print("-" * 50)
        except Exception as e:
            print(f"⚠️ - Identificador não encontrado para o lançamento: {t}")
            print("-" * 50)

    data_fim_processo = datetime.now()
    tempo_processamento = diff_seconds(data_ini_processo, data_fim_processo)
    print(f"[{data_fim_processo.strftime('%Y-%m-%d %H:%M:%S')}] - [INFO] - TOTAL DE TEMPO DE PROCESSAMENTO : {tempo_processamento} SEGUNDOS")