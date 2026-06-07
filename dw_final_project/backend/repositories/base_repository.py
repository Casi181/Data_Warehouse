from database.connection import get_session


class BaseRepository:
    def __init__(self):
        self._session = get_session()

    def _execute(self, query, params=None):
        return self._session.execute(query, params)

    def _prepare(self, query):
        return self._session.prepare(query)
