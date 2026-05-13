# ============================================
# INTEGRAÇÃO - Conecta API com seus serviços
# ============================================

import sys
import os

# Adicionar o path do seu projeto original
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
APP_PATH = os.path.join(PROJECT_ROOT, "app")

if APP_PATH not in sys.path:
    sys.path.insert(0, APP_PATH)

# Importar seus serviços existentes
try:
    from modules.conciliacao_contabil.services.processar_lancamento_service import ProcessarLancamentoService
    from modules.conciliacao_contabil.services.lancamento_service import LancamentoService
    from modules.conciliacao_contabil.services.lancamento_arquivo_service import LancamentoArquivoService
    from modules.conciliacao_contabil.services.classificar_lancamento_service import ClassificarLancamentoService

    SERVICOS_DISPONIVEIS = True
except ImportError as e:
    print(f"Aviso: Serviços originais não encontrados. Usando mocks. Erro: {e}")
    SERVICOS_DISPONIVEIS = False


class IntegracaoService:
    """Ponte entre a API FastAPI e seus serviços existentes"""

    def __init__(self):
        self.processar_service = None
        self.lancamento_service = None
        self.arquivo_service = None
        self.classificar_service = None

        if SERVICOS_DISPONIVEIS:
            self._inicializar_servicos()

    def _inicializar_servicos(self):
        try:
            self.processar_service = ProcessarLancamentoService()
            self.lancamento_service = LancamentoService()
            self.arquivo_service = LancamentoArquivoService()
            self.classificar_service = ClassificarLancamentoService()
        except Exception as e:
            print(f"Erro ao inicializar serviços: {e}")

    async def processar_planilha(self, file_path: str, usuario_id: int) -> dict:
        if not SERVICOS_DISPONIVEIS or not self.processar_service:
            return {
                "total_registros": 0,
                "status": "processando",
                "mensagem": "Serviço de processamento não disponível"
            }

        try:
            resultado = self.processar_service.processar_arquivo(
                caminho_arquivo=file_path,
                usuario_id=usuario_id
            )
            return {
                "total_registros": resultado.get("total", 0),
                "status": "concluido",
                "mensagem": f"Processados {resultado.get('total', 0)} lançamentos"
            }
        except Exception as e:
            return {
                "total_registros": 0,
                "status": "erro",
                "mensagem": f"Erro no processamento: {str(e)}"
            }

    async def listar_lancamentos(self, filtros: dict, page: int = 1, per_page: int = 20):
        if not SERVICOS_DISPONIVEIS or not self.lancamento_service:
            return {"items": [], "total": 0, "page": page, "pages": 0, "per_page": per_page}

        try:
            offset = (page - 1) * per_page
            lancamentos = self.lancamento_service.buscar_com_filtros(
                status=filtros.get("status"),
                data_inicio=filtros.get("data_inicio"),
                data_fim=filtros.get("data_fim"),
                valor_minimo=filtros.get("valor_minimo"),
                valor_maximo=filtros.get("valor_maximo"),
                identificador=filtros.get("identificador"),
                limit=per_page,
                offset=offset
            )

            total = self.lancamento_service.contar_com_filtros(
                status=filtros.get("status"),
                data_inicio=filtros.get("data_inicio"),
                data_fim=filtros.get("data_fim"),
                valor_minimo=filtros.get("valor_minimo"),
                valor_maximo=filtros.get("valor_maximo"),
                identificador=filtros.get("identificador")
            )

            pages = (total + per_page - 1) // per_page

            return {
                "items": [self._converter_lancamento(l) for l in lancamentos],
                "total": total,
                "page": page,
                "pages": pages,
                "per_page": per_page
            }
        except Exception as e:
            print(f"Erro ao listar lançamentos: {e}")
            return {"items": [], "total": 0, "page": page, "pages": 0, "per_page": per_page}

    def _converter_lancamento(self, lancamento) -> dict:
        return {
            "id": getattr(lancamento, "id", 0),
            "data": getattr(lancamento, "data", None),
            "descricao": getattr(lancamento, "descricao", ""),
            "valor": float(getattr(lancamento, "valor", 0)),
            "identificador": getattr(lancamento, "identificador", None),
            "conta_debito": getattr(lancamento, "conta_debito", None),
            "conta_credito": getattr(lancamento, "conta_credito", None),
            "status": getattr(lancamento, "status", "pendente"),
            "grupo_id": getattr(lancamento, "grupo_id", None),
            "arquivo_id": getattr(lancamento, "arquivo_id", None),
            "processado_em": getattr(lancamento, "processado_em", None)
        }

    async def atualizar_status(self, lancamento_id: int, status: str, observacao: str = None):
        if not SERVICOS_DISPONIVEIS or not self.lancamento_service:
            return {"success": False, "message": "Serviço não disponível"}

        try:
            self.lancamento_service.atualizar_status(
                lancamento_id=lancamento_id,
                status=status,
                observacao=observacao
            )
            return {"success": True, "message": "Status atualizado"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    async def obter_estatisticas(self) -> dict:
        if not SERVICOS_DISPONIVEIS or not self.lancamento_service:
            return {
                "total_lancamentos": 0,
                "conciliados": 0,
                "nao_conciliados": 0,
                "pendentes": 0,
                "total_arquivos_processados": 0,
                "ultimos_7_dias": {}
            }

        try:
            stats = self.lancamento_service.obter_estatisticas()
            return {
                "total_lancamentos": stats.get("total", 0),
                "conciliados": stats.get("conciliados", 0),
                "nao_conciliados": stats.get("nao_conciliados", 0),
                "pendentes": stats.get("pendentes", 0),
                "total_arquivos_processados": stats.get("total_arquivos", 0),
                "ultimos_7_dias": stats.get("ultimos_7_dias", {})
            }
        except Exception as e:
            print(f"Erro ao obter estatísticas: {e}")
            return {
                "total_lancamentos": 0,
                "conciliados": 0,
                "nao_conciliados": 0,
                "pendentes": 0,
                "total_arquivos_processados": 0,
                "ultimos_7_dias": {}
            }


integracao = IntegracaoService()
