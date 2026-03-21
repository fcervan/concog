from contextlib import contextmanager
from backend.app.core.database.pool import get_connection


@contextmanager
def get_cursor():

    connection = get_connection()
    cursor = connection.cursor()

    try:
        yield cursor
        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()