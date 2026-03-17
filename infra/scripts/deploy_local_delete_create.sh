#!/bin/bash

set -e

echo "======================================"
echo "🚀 Deploy das Lambdas no LocalStack"
echo "======================================"

LAMBDA_ROLE="arn:aws:iam::000000000000:role/lambda-role"
BUCKET_NAME="concog"
QUEUE_NAME="cc-processar-lancamento"
REGION="us-east-1"

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
        --handler $HANDLER \
        --role $LAMBDA_ROLE \
        --zip-file fileb://$ZIP_FILE
}

echo ""
echo "🪣 Garantindo que o bucket existe..."

if ! awslocal s3api head-bucket --bucket $BUCKET_NAME 2>/dev/null
then
    echo "📦 Criando bucket $BUCKET_NAME"
    awslocal s3 mb s3://$BUCKET_NAME
else
    echo "✅ Bucket já existe"
fi

deploy_lambda "cc-splitar-lancamento" \
"build/cc_splitar_lancamento.zip" \
"handler.lambda_handler"

deploy_lambda "cc-processar-lancamento" \
"build/cc_processar_lancamento.zip" \
"handler.lambda_handler"

echo ""
echo "📨 Garantindo que a fila SQS existe..."

QUEUE_URL=$(awslocal sqs create-queue \
    --queue-name $QUEUE_NAME \
    --query 'QueueUrl' \
    --output text)

echo "Queue URL: $QUEUE_URL"

QUEUE_ARN=$(awslocal sqs get-queue-attributes \
    --queue-url $QUEUE_URL \
    --attribute-names QueueArn \
    --query 'Attributes.QueueArn' \
    --output text)

echo "Queue ARN: $QUEUE_ARN"

echo ""
echo "🔗 Conectando SQS → Lambda cc-processar-lancamento..."

awslocal lambda create-event-source-mapping \
    --function-name cc-processar-lancamento \
    --batch-size 1 \
    --event-source-arn $QUEUE_ARN \
    2>/dev/null || true

echo ""
echo "🔐 Adicionando permissão para S3 invocar a lambda splitar..."

awslocal lambda add-permission \
    --function-name cc-splitar-lancamento \
    --statement-id s3invoke \
    --action lambda:InvokeFunction \
    --principal s3.amazonaws.com \
    --source-arn arn:aws:s3:::$BUCKET_NAME \
    --region $REGION \
    2>/dev/null || true

echo ""
echo "🔎 Obtendo ARN da lambda..."

LAMBDA_ARN=$(awslocal lambda get-function \
    --function-name cc-splitar-lancamento \
    --query 'Configuration.FunctionArn' \
    --output text)

echo "Lambda ARN: $LAMBDA_ARN"


echo ""
echo "⏳ Aguardando serviços estabilizarem..."
sleep 10

echo ""
echo "⚡ Criando trigger S3 → Lambda..."

awslocal s3api put-bucket-notification-configuration \
  --bucket $BUCKET_NAME \
  --notification-configuration "{
    \"LambdaFunctionConfigurations\": [
      {
        \"Id\": \"trigger-xlsx-arquivo-original\",
        \"LambdaFunctionArn\": \"$LAMBDA_ARN\",
        \"Events\": [\"s3:ObjectCreated:*\"] ,
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

echo ""
echo "✅ Deploy finalizado!"