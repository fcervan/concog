# base_repository.py
class BaseRepository:

    def __init__(self, uow):
        self.uow = uow

    def fetch_all(self, query, params=None):
        cursor = self.uow.get_cursor()
        try:
            cursor.execute(query, params or ())
            return cursor.fetchall()
        finally:
            cursor.close()

    def fetch_one(self, query, params=None):
        cursor = self.uow.get_cursor()
        try:
            cursor.execute(query, params or ())
            return cursor.fetchone()
        finally:
            cursor.close()

    def execute(self, query, params=None):
        """
        UPDATE / DELETE
        """
        cursor = self.uow.get_cursor()
        try:
            cursor.execute(query, params or ())
            return cursor.rowcount
        finally:
            cursor.close()

    def insert(self, query, params=None):
        """
        INSERT com retorno de ID
        """
        cursor = self.uow.get_cursor()
        try:
            cursor.execute(query, params or ())
            return cursor.lastrowid
        finally:
            cursor.close()