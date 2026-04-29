import pandas as pd
import os
import re

# =============================
# FUNÇÃO ORIGINAL (mantida)
# =============================
def limpar_csv(arquivo_entrada, arquivo_saida):
    df = pd.read_csv(arquivo_entrada, sep=';', dtype=str)

    # Remove primeira e última linha
    df = df.iloc[1:-1].copy()

    # Seleciona colunas desejadas
    colunas = ['HISTORICO', 'DEBITO', 'CREDITO', 'SALDO']
    df = df[colunas]

    # Limpeza de espaços
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

    # HISTORICO_ID incremental
    df.insert(0, 'HISTORICO_ID', range(1, len(df) + 1))

    # Salva
    df.to_csv(arquivo_saida, sep=';', index=False, encoding='utf-8')


# =============================
# PROCESSAMENTO EM LOTE
# =============================
def processar_diretorio():
    pasta_entrada = "/home/fcervan/Documentos/doc-ai/conciliacao/lancamentos/"
    pasta_saida = "/home/fcervan/Downloads/dataset-csv/"

    # Garante que a pasta de saída existe
    os.makedirs(pasta_saida, exist_ok=True)

    for arquivo in os.listdir(pasta_entrada):
        # Ignorar tudo que não for CSV
        if not arquivo.lower().endswith(".csv"):
            continue

        caminho_entrada = os.path.join(pasta_entrada, arquivo)

        # Extrair número do nome (ex: bloco_1.csv → 1)
        match = re.search(r'(\d+)', arquivo)
        if not match:
            print(f"Arquivo ignorado (sem número): {arquivo}")
            continue

        numero = match.group(1)

        nome_saida = f"lancamento_bruto_{numero}.csv"
        caminho_saida = os.path.join(pasta_saida, nome_saida)

        try:
            limpar_csv(caminho_entrada, caminho_saida)
            print(f"OK: {arquivo} → {nome_saida}")
        except Exception as e:
            print(f"ERRO em {arquivo}: {e}")


# =============================
# EXECUÇÃO
# =============================
if __name__ == "__main__":
    processar_diretorio()