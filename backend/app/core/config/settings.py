import os

try:
    from dotenv import load_dotenv

    # só carrega .env se não estiver rodando na AWS
    if os.getenv("AWS_EXECUTION_ENV") is None:
        load_dotenv()

except ImportError:
    pass


# ==============================
# LLM CONFIG
# ==============================

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")


# GROQ
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "llama3-70b-8192"
)


# HYPERBOLIC

HYPERBOLIC_API_KEY = os.getenv("HYPERBOLIC_API_KEY")
HYPERBOLIC_URL = os.getenv(
    "HYPERBOLIC_URL",
    "https://api.hyperbolic.ai/v1/chat/completions"
)
HYPERBOLIC_MODEL = os.getenv(
    "HYPERBOLIC_MODEL",
    "meta-llama/Meta-Llama-3-70B-Instruct"
)


# ==============================
# DATABASE CONFIG
# ==============================

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "concog")

# pool de conexões
DB_POOL_NAME = os.getenv("DB_POOL_NAME", "concog_pool")
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", 5))