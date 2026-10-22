from contextlib import contextmanager

import psycopg2


class NumberRepository:
    def __init__(self, dsn):
        self.dsn = dsn

    @contextmanager
    def _cursor(self):
        conn = psycopg2.connect(self.dsn)
        try:
            with conn:  # commit при успехе, rollback при исключении
                with conn.cursor() as cur:
                    yield cur
        finally:
            conn.close()

    def exists(self, n):
        with self._cursor() as cur:
            cur.execute("SELECT 1 FROM processed_numbers WHERE num = %s", (n,))
            return cur.fetchone() is not None

    def save(self, n):
        # вернет False, если число уже есть (сработал UNIQUE)
        with self._cursor() as cur:
            cur.execute(
                "INSERT INTO processed_numbers (num) VALUES (%s) ON CONFLICT (num) DO NOTHING",
                (n,),
            )
            return cur.rowcount == 1
