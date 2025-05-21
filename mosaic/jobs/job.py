import json
from pathlib import Path
from typing import Self
from uuid import UUID, uuid4

from mosaic.jobs.utils import MOSAIC_TEMP_DIR


class Job:
    info_fname = 'job.json'

    def __init__(
        self,
        *,
        command: str,
        id: UUID,
        input_file: Path,
        output_file: Path,
    ) -> None:
        self.command = command
        self.id = id
        self.input_file = input_file
        self.output_file = output_file
        self._dirname = f'{self.id}'
        self._dirpath = MOSAIC_TEMP_DIR / self._dirname

    def create_dirs(self) -> None:
        Path.mkdir(self._dirpath, parents=True)

    def start(self) -> None:
        print(f'\nStarted job {self.id}')
        print(f'{self.command} -i {self.input_file} {self.output_file}')

    @classmethod
    def create(cls, *, command: str, input_file: Path, output_file: Path) -> Self:
        job = cls(
            command=command,
            id=uuid4(),
            input_file=input_file,
            output_file=output_file,
        )
        return job

    @classmethod
    def load(cls, dirpath: Path) -> Self:
        fpath = dirpath / cls.info_fname
        with open(fpath, 'r') as f:
            d = json.load(f)
        return cls(
            command=d['command'],
            id=UUID(d['id']),
            input_file=Path(d['input_file']),
            output_file=Path(d['output_file']),
        )

    def save(self) -> None:
        info_fpath = self._dirpath / self.info_fname
        info = {k: str(v) for k, v in dict(
            command=self.command,
            id=self.id,
            input_file=self.input_file,
            output_file=self.output_file,
        ).items()}
        with open(info_fpath, 'w') as f:
            json.dump(info, f, indent=4)
