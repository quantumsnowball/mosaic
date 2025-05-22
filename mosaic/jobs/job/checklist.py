from pathlib import Path
from sqlite3 import Connection, connect

Entry = tuple[str, int]
Entries = list[Entry]


class Task:
    def __init__(self, name: str, done: int) -> None:
        self.name = str(name)
        self.done = bool(done)


class Tasks:
    def __init__(self, entries: Entries) -> None:
        self.items = tuple(Task(*e) for e in entries)

    @property
    def count(self) -> int:
        return len(self.items)


class Checklist:
    name = 'checklist'

    def __init__(
        self,
        path: Path
    ) -> None:
        self.path = path

    @property
    def database(self) -> Connection:
        return connect(self.path)

    @property
    def tasks(self) -> Tasks:
        sql = f'SELECT name, done FROM {self.name}'
        with self.database as db:
            entries = db.execute(sql).fetchall()
            return Tasks(entries)

    def create(self) -> None:
        sql = (
            f'CREATE TABLE IF NOT EXISTS {self.name} ('
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

    # helpers
    def next_task(self) -> Task | None:
        sql = f'SELECT * FROM {self.name} WHERE done = 0 ORDER BY name LIMIT 1'
        with self.database as db:
            entry: Entry | None = db.execute(sql).fetchone()
        return Task(*entry) if entry else None

    def mark_done(self, task: Task) -> None:
        sql = f'UPDATE {self.name} SET done = 1 WHERE name = ?'
        with self.database as db:
            db.execute(sql, (task.name, ))
