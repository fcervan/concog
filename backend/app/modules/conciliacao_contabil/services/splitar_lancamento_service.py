import mysql.connector
import json


class SplitarLancamentoService:

    def processar(self, event):
        print("Iniciando conexão com o MySQL no host...")

        connection = None
        try:
            # IMPORTANTE: Usamos o IP 172.17.0.1 para sair do container Lambda
            # e acessar a porta 3307 do seu Ubuntu
            connection = mysql.connector.connect(
                host='172.17.0.1',
                port=3307,
                user='root',
                password='123456',
                database='concog'
            )

            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM tipo_usuario")
            resultados = cursor.fetchall()

            print(f"Sucesso! Registros encontrados XXXXXXXXXXXXXXXXXX: {len(resultados)}")

            response = {
                "status": "ok",
                "acao": "splitar_lancamento",
                "dados": resultados
            }
            print(response)

            return response

        except mysql.connector.Error as err:
            print(f"Erro ao conectar ou consultar o banco: {err}")
            return {
                "status": "erro",
                "mensagem": str(err)
            }

        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
                print("Conexão MySQL encerrada.")
