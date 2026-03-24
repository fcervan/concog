from backend.app.core.database.base_repository import BaseRepository


class LancamentoArquivoRepository(BaseRepository):

    def inserir(self, cliente_id, usuario_id, s3_path, data_cad):
        query = f"""
            INSERT INTO concog.lancamento_arquivo (cliente_id, usuario_id, s3_path, data_cad)
            VALUES (%s,%s,%s,%s);
        """
        return self.insert(query,(cliente_id, usuario_id, s3_path, data_cad))