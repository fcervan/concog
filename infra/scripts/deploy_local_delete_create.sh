#!/bin/bash

set -e

echo "======================================"
echo "🚀 Deploy das Lambdas no LocalStack"
echo "======================================"

#############################################
# 🌍 CONFIG GLOBAL
#############################################

export AWS_DEFAULT_REGION=us-east-1
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_ENDPOINT_URL=http://localhost.localstack.cloud:4566

LAMBDA_ROLE="arn:aws:iam::000000000000:role/lambda-role"
BUCKET_NAME="concog"
QUEUE_NAME="cc-processar-lancamento"

BUILD_DIR="build"

#############################################
# 🛠️ Função para build da lambda
#############################################
build_lambda () {

    FUNCTION_NAME=$1

    echo ""
    echo "🔨 Build da lambda: $FUNCTION_NAME"

    rm -rf $BUILD_DIR/$FUNCTION_NAME
    mkdir -p $BUILD_DIR/$FUNCTION_NAME

    cp -r backend $BUILD_DIR/$FUNCTION_NAME/

    if [ -f requirements.txt ]; then
        pip install -r requirements.txt -t $BUILD_DIR/$FUNCTION_NAME > /dev/null
    fi

    cd $BUILD_DIR/$FUNCTION_NAME
    zip -r ../$FUNCTION_NAME.zip . > /dev/null
    cd - > /dev/null

    echo "✅ Build concluído: $BUILD_DIR/$FUNCTION_NAME.zip"
}

#############################################
# 🚀 Deploy da lambda
#############################################
deploy_lambda () {

    FUNCTION_NAME=$1
    ZIP_FILE=$2
    HANDLER=$3

    echo ""
    echo "📦 Deploy da lambda: $FUNCTION_NAME"

    if awslocal lambda get-function --function-name $FUNCTION_NAME > /dev/null 2>&1
    then
        echo "🧹 Deletando lambda antiga..."
        awslocal lambda delete-function \
            --function-name $FUNCTION_NAME
    fi

    echo "✨ Criando lambda..."

    awslocal lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime python3.11 \
        --timeout 600 \
        --memory-size 1024 \
        --handler $HANDLER \
        --role $LAMBDA_ROLE \
        --environment file://infra/scripts/env.json \
        --zip-file fileb://$ZIP_FILE

    echo "⏳ Aguardando lambda ficar ativa..."
    awslocal lambda wait function-active \
        --function-name $FUNCTION_NAME

    echo "✅ Lambda pronta"
}

#############################################
# 🪣 S3
#############################################

echo ""
echo "🪣 Garantindo bucket..."

if ! awslocal s3api head-bucket --bucket $BUCKET_NAME 2>/dev/null
then
    echo "📦 Criando bucket..."
    awslocal s3 mb s3://$BUCKET_NAME
else
    echo "✅ Bucket já existe"
fi

#############################################
# 🔨 BUILD
#############################################

build_lambda "cc_splitar_lancamento"
build_lambda "cc_processar_lancamento"

#############################################
# 🚀 DEPLOY
#############################################

deploy_lambda "cc-splitar-lancamento" \
"$BUILD_DIR/cc_splitar_lancamento.zip" \
"backend.app.modules.conciliacao_contabil.lambdas.cc_splitar_lancamento.handler.lambda_handler"

deploy_lambda "cc-processar-lancamento" \
"$BUILD_DIR/cc_processar_lancamento.zip" \
"backend.app.modules.conciliacao_contabil.lambdas.cc_processar_lancamento.handler.lambda_handler"

#############################################
# 📨 SQS
#############################################

echo ""
echo "📨 Garantindo fila SQS..."

QUEUE_URL=$(awslocal --endpoint-url=$AWS_ENDPOINT_URL sqs create-queue \
    --queue-name $QUEUE_NAME \
    --query 'QueueUrl' \
    --output text)

QUEUE_ARN=$(awslocal --endpoint-url=$AWS_ENDPOINT_URL sqs get-queue-attributes \
    --queue-url $QUEUE_URL \
    --attribute-names QueueArn \
    --query 'Attributes.QueueArn' \
    --output text)

echo "Queue ARN: $QUEUE_ARN"

#############################################
# 🔗 SQS → Lambda
#############################################

echo ""
echo "🔗 Conectando SQS → Lambda..."

awslocal lambda create-event-source-mapping \
    --function-name cc-processar-lancamento \
    --batch-size 1 \
    --event-source-arn $QUEUE_ARN \
    2>/dev/null || echo "ℹ️ Mapping já existe"

#############################################
# 🔐 Permissão S3 → Lambda (CORRIGIDO)
#############################################

echo ""
echo "🔐 Configurando permissão S3 → Lambda..."

awslocal lambda add-permission \
    --function-name cc-splitar-lancamento \
    --statement-id s3invoke \
    --action lambda:InvokeFunction \
    --principal s3.amazonaws.com \
    2>/dev/null || echo "ℹ️ Permissão já existe"

#############################################
# 🔎 ARN
#############################################

echo ""
echo "🔎 Obtendo ARN da lambda..."

LAMBDA_ARN=$(awslocal lambda get-function \
    --function-name cc-splitar-lancamento \
    --query 'Configuration.FunctionArn' \
    --output text)

echo "Lambda ARN: $LAMBDA_ARN"

#############################################
# ⚡ Trigger S3 → Lambda (CORRIGIDO)
#############################################

echo ""
echo "⚡ Criando trigger S3 → Lambda..."

awslocal s3api put-bucket-notification-configuration \
  --bucket $BUCKET_NAME \
  --notification-configuration "{
    \"LambdaFunctionConfigurations\": [
      {
        \"Id\": \"trigger-xlsx-arquivo-original\",
        \"LambdaFunctionArn\": \"$LAMBDA_ARN\",
        \"Events\": [\"s3:ObjectCreated:*\"],
        \"Filter\": {
          \"Key\": {
            \"FilterRules\": [
              {
                \"Name\": \"prefix\",
                \"Value\": \"cc/arquivo-original/\"
              },
              {
                \"Name\": \"suffix\",
                \"Value\": \".xlsx\"
              }
            ]
          }
        }
      }
    ]
  }"

#############################################
# 🔍 DEBUG FINAL
#############################################

echo ""
echo "🔍 Validando configuração..."

awslocal s3api get-bucket-notification-configuration \
  --bucket $BUCKET_NAME

echo ""
echo "✅ Deploy finalizado com sucesso!"