#!/bin/bash

echo "Invocando cc-splitar-lancamento..."

awslocal lambda invoke \
  --function-name cc-splitar-lancamento \
  --payload '{}' \
  response_splitar.json

cat response_splitar.json

echo ""
echo "Invocando cc-processar-lancamento..."

awslocal lambda invoke \
  --function-name cc-processar-lancamento \
  --payload '{}' \
  response_processar.json

cat response_processar.json
