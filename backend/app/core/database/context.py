from contextlib import contextmanager
from backend.app.core.database.pool import get_connection


@contextmanager
def get_cursor(dictionary=True):

    connection = get_connection()
    cursor = connection.cursor(dictionary=dictionary)

    try:
        yield cursor
        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()