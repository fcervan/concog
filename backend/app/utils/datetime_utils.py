from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Timezone padrão do projeto (São Paulo)
SAO_PAULO_TZ = ZoneInfo("America/Sao_Paulo")


# ==========================================================
# 1. Funções básicas de data/hora
# ==========================================================

def now_sp() -> datetime:
    """
    Retorna a data/hora atual no fuso de São Paulo.
    """
    return datetime.now(SAO_PAULO_TZ)


def now_sp_str(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Retorna a data/hora atual de São Paulo formatada como string.
    """
    return now_sp().strftime(fmt)


def format_date(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Formata um datetime para string usando o formato informado.
    """
    return dt.strftime(fmt)


def parse_date(date_str: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """
    Converte uma string em objeto datetime no formato informado.
    """
    return datetime.strptime(date_str, fmt)


# ==========================================================
# 2. Timezone: garantir, aplicar e converter fusos
# ==========================================================

def ensure_tz(dt: datetime, tz: str = "UTC") -> datetime:
    """
    Garante que o datetime tenha timezone (timezone-aware).
    Se for naive, aplica o timezone informado.
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=ZoneInfo(tz))
    return dt


def to_timezone(dt: datetime, tz: str = "America/Sao_Paulo") -> datetime:
    """
    Converte um datetime para um fuso horário específico.
    """
    dt = ensure_tz(dt, tz="UTC")  # sempre garante consistência
    return dt.astimezone(ZoneInfo(tz))


# ==========================================================
# 3. Datas financeiras/contábeis
# ==========================================================

def first_day_of_month(dt: datetime | None = None) -> datetime:
    """
    Retorna o primeiro dia do mês da data informada (ou atual).
    """
    dt = dt or now_sp()
    return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def last_day_of_month(dt: datetime | None = None) -> datetime:
    """
    Retorna o último dia do mês da data informada (ou atual).
    """
    dt = dt or now_sp()

    # truque: adiciona 4 dias ao dia 28, sempre cai no próximo mês
    next_month = dt.replace(day=28) + timedelta(days=4)
    # 1º dia do próximo mês menos 1 segundo
    return next_month.replace(day=1, hour=23, minute=59, second=59, microsecond=999999) - timedelta(seconds=0)


# ==========================================================
# 4. Utilidades diversas
# ==========================================================

def diff_seconds(start: datetime, end: datetime) -> float:
    """
    Retorna a diferença entre duas datas em segundos.
    """
    return (end - start).total_seconds()


def timestamp_ms() -> int:
    """
    Retorna timestamp atual em milissegundos.
    Útil para logs, auditoria e mensagens SQS.
    """
    return int(now_sp().timestamp() * 1000)