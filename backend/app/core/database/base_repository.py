from backend.app.core.database.context import get_cursor


class BaseRepository:

    def fetch_all(self, query, params=None):

        with get_cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchall()

    def fetch_one(self, query, params=None):

        with get_cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchone()

    def execute(self, query, params=None):

        with get_cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.rowcount