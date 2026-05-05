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
# 🛠️ BUILD
#############################################

build_lambda () {

    FUNCTION_NAME=$1

    echo ""
    echo "🔨 Build da lambda: $FUNCTION_NAME"

    rm -rf $BUILD_DIR/$FUNCTION_NAME
    mkdir -p $BUILD_DIR/$FUNCTION_NAME

    cp -r backend $BUILD_DIR/$FUNCTION_NAME/

    if [ -f requirements.txt ]; then
        pip install -r requirements.txt \
            -t $BUILD_DIR/$FUNCTION_NAME \
            > /dev/null
    fi

    cd $BUILD_DIR/$FUNCTION_NAME

    zip -r ../$FUNCTION_NAME.zip . > /dev/null

    cd - > /dev/null

    echo "✅ Build concluído"
}

#############################################
# 🚀 DEPLOY LAMBDA
#############################################

deploy_lambda () {

    FUNCTION_NAME=$1
    ZIP_FILE=$2
    HANDLER=$3

    echo ""
    echo "📦 Deploy da lambda: $FUNCTION_NAME"

    if awslocal lambda get-function \
        --function-name $FUNCTION_NAME \
        > /dev/null 2>&1
    then

        echo "♻️ Atualizando lambda existente..."

        awslocal lambda update-function-code \
            --function-name $FUNCTION_NAME \
            --zip-file fileb://$ZIP_FILE

    else

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
    fi

    echo "⏳ Aguardando lambda..."

    awslocal lambda wait function-active \
        --function-name $FUNCTION_NAME

    echo "✅ Lambda pronta"
}

#############################################
# 🪣 S3
#############################################

echo ""
echo "🪣 Garantindo bucket..."

if ! awslocal s3api head-bucket \
    --bucket $BUCKET_NAME \
    > /dev/null 2>&1
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

deploy_lambda \
    "cc-splitar-lancamento" \
    "$BUILD_DIR/cc_splitar_lancamento.zip" \
    "backend.app.modules.conciliacao_contabil.lambdas.cc_splitar_lancamento.handler.lambda_handler"

deploy_lambda \
    "cc-processar-lancamento" \
    "$BUILD_DIR/cc_processar_lancamento.zip" \
    "backend.app.modules.conciliacao_contabil.lambdas.cc_processar_lancamento.handler.lambda_handler"

#############################################
# 📨 SQS
#############################################

echo ""
echo "📨 Garantindo fila SQS..."

QUEUE_URL=$(awslocal sqs create-queue \
    --queue-name $QUEUE_NAME \
    --query 'QueueUrl' \
    --output text)

QUEUE_ARN=$(awslocal sqs get-queue-attributes \
    --queue-url $QUEUE_URL \
    --attribute-names QueueArn \
    --query 'Attributes.QueueArn' \
    --output text)

echo "Queue URL: $QUEUE_URL"
echo "Queue ARN: $QUEUE_ARN"

#############################################
# 🔗 SQS → Lambda
#############################################

echo ""
echo "🔗 Configurando SQS → Lambda..."

echo "⏳ Aguardando estabilização..."
sleep 20

echo ""
echo "🧹 Limpando mappings antigos..."

MAPPING_UUIDS=$(awslocal lambda list-event-source-mappings \
    --event-source-arn "$QUEUE_ARN" \
    --query 'EventSourceMappings[*].UUID' \
    --output text)

if [ -n "$MAPPING_UUIDS" ] && [ "$MAPPING_UUIDS" != "None" ]; then

    for UUID in $MAPPING_UUIDS
    do
        echo "Removendo mapping: $UUID"

        awslocal lambda delete-event-source-mapping \
            --uuid "$UUID"
    done

    sleep 5
fi

echo ""
echo "✨ Criando novo mapping..."

awslocal lambda create-event-source-mapping \
    --function-name cc-processar-lancamento \
    --batch-size 1 \
    --enabled \
    --event-source-arn "$QUEUE_ARN"

echo ""
echo "🔍 Validando mapping..."

MAPPING_STATE=$(awslocal lambda list-event-source-mappings \
    --function-name cc-processar-lancamento \
    --query 'EventSourceMappings[0].State' \
    --output text)

if [ "$MAPPING_STATE" != "Enabled" ]; then
    echo "❌ Mapping não ficou ativo."
    echo "Estado atual: $MAPPING_STATE"
    exit 1
fi

echo "✅ Mapping ativo"

#############################################
# 🔐 PERMISSÃO S3 → Lambda
#############################################

echo ""
echo "🔐 Configurando permissão S3..."

awslocal lambda add-permission \
    --function-name cc-splitar-lancamento \
    --statement-id s3invoke \
    --action lambda:InvokeFunction \
    --principal s3.amazonaws.com \
    > /dev/null 2>&1 || true

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
# ⚡ S3 → Lambda
#############################################

echo ""
echo "⚡ Criando trigger S3..."

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
echo "=============================="
echo "🔍 DEBUG FINAL"
echo "=============================="

echo ""
echo "S3 Trigger:"
awslocal s3api get-bucket-notification-configuration \
    --bucket $BUCKET_NAME

echo ""
echo "SQS Mapping:"
awslocal lambda list-event-source-mappings \
    --function-name cc-processar-lancamento

echo ""
echo "✅ Deploy finalizado com sucesso!"