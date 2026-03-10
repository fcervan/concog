#!/bin/bash

set -e

echo "======================================"
echo "🚀 Deploy das Lambdas no LocalStack"
echo "======================================"

LAMBDA_ROLE="arn:aws:iam::000000000000:role/lambda-role"

deploy_lambda () {

    FUNCTION_NAME=$1
    ZIP_FILE=$2
    HANDLER=$3

    echo ""
    echo "📦 Deploy da lambda: $FUNCTION_NAME"

    if awslocal lambda get-function --function-name $FUNCTION_NAME > /dev/null 2>&1
    then
        echo "🔄 Lambda já existe. Atualizando código..."

        awslocal lambda update-function-code \
            --function-name $FUNCTION_NAME \
            --zip-file fileb://$ZIP_FILE

    else
        echo "✨ Criando nova lambda..."

        awslocal lambda create-function \
            --function-name $FUNCTION_NAME \
            --runtime python3.11 \
            --timeout 600 \
            --handler $HANDLER \
            --role $LAMBDA_ROLE \
            --zip-file fileb://$ZIP_FILE
    fi

}

deploy_lambda "cc-splitar-lancamento" \
"build/cc_splitar_lancamento.zip" \
"handler.lambda_handler"

deploy_lambda "cc-processar-lancamento" \
"build/cc_processar_lancamento.zip" \
"handler.lambda_handler"

echo ""
echo "✅ Deploy finalizado!"
