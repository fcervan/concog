#!/bin/bash

set -e

echo "=============================="
echo "Build das Lambdas - ConCog"
echo "=============================="

rm -rf build
mkdir -p build

########################################
# Lambda cc_splitar_lancamento
########################################

echo "Preparando cc_splitar_lancamento..."

mkdir -p build/cc_splitar_tmp

pip install -r requirements.txt -t build/cc_splitar_tmp/

cp -r backend build/cc_splitar_tmp/

cp backend/app/modules/conciliacao_contabil/lambdas/cc_splitar_lancamento/handler.py \
build/cc_splitar_tmp/handler.py

cd build/cc_splitar_tmp
zip -r ../cc_splitar_lancamento.zip .
cd ../..

rm -rf build/cc_splitar_tmp

########################################
# Lambda cc_processar_lancamento
########################################

echo "Preparando cc_processar_lancamento..."

mkdir -p build/cc_processar_tmp

pip install -r requirements.txt -t build/cc_processar_tmp/

cp -r backend build/cc_processar_tmp/

cp backend/app/modules/conciliacao_contabil/lambdas/cc_processar_lancamento/handler.py \
build/cc_processar_tmp/handler.py

cd build/cc_processar_tmp
zip -r ../cc_processar_lancamento.zip .
cd ../..

rm -rf build/cc_processar_tmp

echo "Build finalizado."