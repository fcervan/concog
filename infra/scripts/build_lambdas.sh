#!/bin/bash

set -e

PROJECT_ROOT=$(pwd)

echo "Limpando builds anteriores..."
rm -rf build
mkdir build

echo "Instalando dependências..."
pip install -r backend/requirements.txt -t build/

echo "Copiando código backend..."
cp -r backend build/

echo "Criando ZIP cc-splitar-lancamento..."

cd build
zip -r ../cc-splitar-lancamento.zip .

cd $PROJECT_ROOT

echo "Criando ZIP cc-processar-lancamento..."

cp cc-splitar-lancamento.zip cc-processar-lancamento.zip

echo "Build finalizado."
