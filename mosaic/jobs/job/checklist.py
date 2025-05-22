from pathlib import Path
from sqlite3 import Connection, connect


class Checklist:
    def __init__(
        self,
        path: Path
    ) -> None:
        self.path = path

    @property
    def database(self) -> Connection:
        return connect(self.path)

    def create(self) -> None:
        sql = (
            'CREATE TABLE IF NOT EXISTS checklist ('
            '   name TEXT PRIMARY KEY,'
            '   done BOOLEAN NOT NULL'
            ');'
        )
        with self.database as db:
            db.execute(sql)

    def initialize(
        self,
        target_dir: Path,
        *,
        ext: str,
        val: bool,
    ) -> None:
        sql = 'INSERT INTO checklist (name, done) VALUES (?, ?)'
        with self.database as db:
            for f in sorted(target_dir.glob(f'*.{ext}')):
                db.execute(sql, (f.name, val))
