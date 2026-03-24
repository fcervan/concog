# unit_of_work.py
from backend.app.core.database.pool import get_connection


class UnitOfWork:

    def __init__(self):
        self.conn = None

    def __enter__(self):
        self.conn = get_connection()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type:
                self.conn.rollback()
            else:
                self.conn.commit()
        finally:
            self.conn.close()

    def get_cursor(self):
        return self.conn.cursor()