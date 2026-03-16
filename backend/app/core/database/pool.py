import mysql.connector
from mysql.connector import pooling
from backend.app.core.config import settings


connection_pool = pooling.MySQLConnectionPool(
    pool_name=settings.DB_POOL_NAME,
    pool_size=settings.DB_POOL_SIZE,
    host=settings.DB_HOST,
    port=settings.DB_PORT,
    user=settings.DB_USER,
    password=settings.DB_PASSWORD,
    database=settings.DB_NAME
)


def get_connection():
    return connection_pool.get_connection()