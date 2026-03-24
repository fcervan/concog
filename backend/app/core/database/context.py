# context.py
from backend.app.core.database.pool import get_connection


def get_connection_context():
    return get_connection()