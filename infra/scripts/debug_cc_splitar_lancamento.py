from backend.app.modules.conciliacao_contabil.lambdas.cc_splitar_lancamento.handler import lambda_handler


evento_fake = {
    "Records": [
        {
            "s3": {
                "bucket": {
                    "name": "concog"
                },
                "object": {
                    "key": "nao-conciliado-um-lancamento-grande.xlsx"
                }
            }
        }
    ]
}


lambda_handler(
    event=evento_fake,
    context=None
)