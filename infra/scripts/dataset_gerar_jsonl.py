import json
import os
from pathlib import Path

# Configurações dos diretórios
DIR_BRUTO = "/home/fcervan/Downloads/dataset-csv/bruto/"
DIR_CLASSIFICADO = "/home/fcervan/Downloads/dataset-csv/classificado/"

# Lista de arquivos classificados que você quer usar
# Preencha apenas com os nomes dos arquivos que deseja processar
lista_arquivos_classificados = [
    "lancamento_classificado_124.csv",
    "lancamento_classificado_77.csv",
    "lancamento_classificado_76.csv",
    "lancamento_classificado_94.csv",
    "lancamento_classificado_61.csv",
    "lancamento_classificado_85.csv",
    "lancamento_classificado_53.csv",
    "lancamento_classificado_31.csv",
    "lancamento_classificado_78.csv",
    "lancamento_classificado_62.csv",
    "lancamento_classificado_125.csv",
    "lancamento_classificado_74.csv",
    "lancamento_classificado_35.csv",
    "lancamento_classificado_19.csv",
    "lancamento_classificado_129.csv",
    "lancamento_classificado_107.csv",
    "lancamento_classificado_97.csv",
    "lancamento_classificado_95.csv",
    "lancamento_classificado_87.csv",
    "lancamento_classificado_75.csv",
    "lancamento_classificado_44.csv",
    "lancamento_classificado_38.csv",
    "lancamento_classificado_34.csv",
    "lancamento_classificado_11.csv",
    "lancamento_classificado_81.csv",
    "lancamento_classificado_80.csv",
    "lancamento_classificado_50.csv",
    "lancamento_classificado_27.csv",
    "lancamento_classificado_16.csv",
    "lancamento_classificado_116.csv",
    "lancamento_classificado_109.csv",
    "lancamento_classificado_106.csv",
    "lancamento_classificado_104.csv",
    "lancamento_classificado_101.csv",
    "lancamento_classificado_9.csv",
    "lancamento_classificado_99.csv",
    "lancamento_classificado_92.csv",
    "lancamento_classificado_90.csv",
    "lancamento_classificado_82.csv",
    "lancamento_classificado_70.csv",
    "lancamento_classificado_65.csv",
    "lancamento_classificado_63.csv",
    "lancamento_classificado_58.csv",
    "lancamento_classificado_56.csv",
    "lancamento_classificado_51.csv",
    "lancamento_classificado_4.csv",
    "lancamento_classificado_40.csv",
    "lancamento_classificado_66.csv",
    "lancamento_classificado_59.csv",
    "lancamento_classificado_52.csv",
    "lancamento_classificado_46.csv",
    "lancamento_classificado_43.csv",
    "lancamento_classificado_41.csv",
    "lancamento_classificado_36.csv",
    "lancamento_classificado_33.csv",
    "lancamento_classificado_32.csv",
    "lancamento_classificado_29.csv",
    "lancamento_classificado_24.csv",
    "lancamento_classificado_22.csv",
    "lancamento_classificado_21.csv",
    "lancamento_classificado_17.csv",
    "lancamento_classificado_140.csv",
    "lancamento_classificado_138.csv",
    "lancamento_classificado_122.csv",
    "lancamento_classificado_121.csv",
    "lancamento_classificado_111.csv",
    "lancamento_classificado_10.csv"
]

# Arquivo de saída do dataset
ARQUIVO_SAIDA = "/home/fcervan/Downloads/dataset-csv/dataset.jsonl"


def ler_conteudo_arquivo(caminho_arquivo):
    """Lê o conteúdo completo de um arquivo e retorna como string."""
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"ERRO: Arquivo não encontrado: {caminho_arquivo}")
        return None
    except Exception as e:
        print(f"ERRO ao ler arquivo {caminho_arquivo}: {e}")
        return None


def extrair_numero_arquivo(nome_arquivo_classificado):
    """Extrai o número do arquivo classificadopara encontrar o correspondente bruto."""
    # Remove 'lancamento_classificado_' e '.csv' para obter o número
    nome_sem_prefixo = nome_arquivo_classificado.replace('lancamento_classificado_', '')
    numero = nome_sem_prefixo.replace('.csv', '')
    return numero


def gerar_dataset():
    """Gera o arquivo de dataset no formato JSONL."""
    registros_processados = 0
    registros_ignorados = 0

    with open(ARQUIVO_SAIDA, 'w', encoding='utf-8') as arquivo_saida:
        for arquivo_classificado in lista_arquivos_classificados:
            print(f"\nProcessando: {arquivo_classificado}")

            # Extrai o número do arquivo classificado
            numero = extrair_numero_arquivo(arquivo_classificado)

            # Monta o nome do arquivo bruto correspondente
            arquivo_bruto = f"lancamento_bruto_{numero}.csv"

            # Caminhos completos
            caminho_classificado = os.path.join(DIR_CLASSIFICADO, arquivo_classificado)
            caminho_bruto = os.path.join(DIR_BRUTO, arquivo_bruto)

            # Verifica se ambos os arquivos existem
            if not os.path.exists(caminho_classificado):
                print(f"  AVISO: Arquivo classificado não encontrado: {caminho_classificado}")
                registros_ignorados += 1
                continue

            if not os.path.exists(caminho_bruto):
                print(f"  AVISO: Arquivo bruto correspondente não encontrado: {caminho_bruto}")
                registros_ignorados += 1
                continue

            # Lê o conteúdo dos arquivos
            conteudo_input = ler_conteudo_arquivo(caminho_bruto)
            conteudo_output = ler_conteudo_arquivo(caminho_classificado)

            if conteudo_input is None or conteudo_output is None:
                registros_ignorados += 1
                continue

            # Cria o registro no formato desejado
            registro = {
                "instruction": "Agrupe os lançamentos contábeis relacionados. Separe cada grupo com duas quebras de linha.",
                "input": conteudo_input,
                "output": conteudo_output
            }

            # Escreve no arquivo de saída (formato JSONL - um JSON por linha)
            arquivo_saida.write(json.dumps(registro, ensure_ascii=False) + '\n')
            registros_processados += 1
            print(f"  ✓ Processado com sucesso (par {numero})")

    print(f"\n" + "=" * 50)
    print(f"RESUMO:")
    print(f"  - Registros processados com sucesso: {registros_processados}")
    print(f"  - Registros ignorados (erros/ausentes): {registros_ignorados}")
    print(f"  - Arquivo de saída: {ARQUIVO_SAIDA}")
    print("=" * 50)


def listar_arquivos_disponiveis():
    """Função auxiliar para listar todos os arquivos disponíveis nos diretórios."""
    print("\nArquivos disponíveis no diretório BRUTO:")
    if os.path.exists(DIR_BRUTO):
        arquivos_bruto = sorted([f for f in os.listdir(DIR_BRUTO) if f.endswith('.csv')])
        for arquivo in arquivos_bruto:
            print(f"  - {arquivo}")
    else:
        print(f"  Diretório não encontrado: {DIR_BRUTO}")

    print("\nArquivos disponíveis no diretório CLASSIFICADO:")
    if os.path.exists(DIR_CLASSIFICADO):
        arquivos_classificado = sorted([f for f in os.listdir(DIR_CLASSIFICADO) if f.endswith('.csv')])
        for arquivo in arquivos_classificado:
            print(f"  - {arquivo}")
    else:
        print(f"  Diretório não encontrado: {DIR_CLASSIFICADO}")


if __name__ == "__main__":
    print("GERADOR DE DATASET - LANÇAMENTOS CONTÁBEIS")
    print("=" * 50)

    # Opção para listar arquivos disponíveis (útil para preencher a lista)
    resposta = input("Deseja listar os arquivos disponíveis nos diretórios? (s/N): ")
    if resposta.lower() == 's':
        listar_arquivos_disponiveis()
        print("\n" + "=" * 50)

    # Confirmação antes de gerar
    print(f"\nArquivos a serem processados: {len(lista_arquivos_classificados)}")
    resposta = input("Deseja gerar o dataset? (s/N): ")

    if resposta.lower() == 's':
        gerar_dataset()
    else:
        print("Operação cancelada.")