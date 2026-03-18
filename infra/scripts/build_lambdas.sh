#!/bin/bash

set -e

echo "=============================="
echo "Build das Lambdas - ConCog (OTIMIZADO)"
echo "=============================="

BUILD_DIR="build"
COMMON_DIR="$BUILD_DIR/common"

rm -rf $BUILD_DIR
mkdir -p $COMMON_DIR

########################################
# 1. Instala dependências UMA vez
########################################

echo "Instalando dependências..."

pip install -r requirements.txt -t $COMMON_DIR

########################################
# 2. Limpeza pesada (ESSENCIAL)
########################################

echo "Limpando arquivos desnecessários..."

cd $COMMON_DIR

# Remove caches e testes
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type d -name "tests" -exec rm -rf {} +

# Remove metadados pesados
find . -type d -name "*.dist-info" -exec rm -rf {} +
find . -type d -name "*.egg-info" -exec rm -rf {} +

# Remove arquivos compilados
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete

cd ../..

########################################
# Função genérica para build de lambda
########################################

build_lambda () {
    FUNCTION_NAME=$1
    HANDLER_PATH=$2

    echo "Preparando $FUNCTION_NAME..."

    TMP_DIR="$BUILD_DIR/${FUNCTION_NAME}_tmp"
    ZIP_PATH="$BUILD_DIR/${FUNCTION_NAME}.zip"

    mkdir -p $TMP_DIR

    # Copia libs já limpas
    cp -r $COMMON_DIR/* $TMP_DIR/

    # ⚠️ Copiar somente o necessário do backend
    mkdir -p $TMP_DIR/backend/app/modules/conciliacao_contabil

    cp -r backend/app/modules/conciliacao_contabil $TMP_DIR/backend/app/modules/

    # Copia handler
    cp $HANDLER_PATH $TMP_DIR/handler.py

    ########################################
    # Limpeza final (extra segurança)
    ########################################
    cd $TMP_DIR

    find . -type d -name "__pycache__" -exec rm -rf {} +
    find . -name "*.pyc" -delete

    ########################################
    # Zip
    ########################################
    zip -rq ../$(basename $ZIP_PATH) .

    cd ../../
    rm -rf $TMP_DIR
}

########################################
# 3. Build das lambdas
########################################

build_lambda \
  "cc_splitar_lancamento" \
  "backend/app/modules/conciliacao_contabil/lambdas/cc_splitar_lancamento/handler.py"

build_lambda \
  "cc_processar_lancamento" \
  "backend/app/modules/conciliacao_contabil/lambdas/cc_processar_lancamento/handler.py"

echo "Build finalizado com sucesso."