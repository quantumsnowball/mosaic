import json
from pathlib import Path
from types import SimpleNamespace as NS
from typing import Self
from uuid import UUID, uuid4

import ffmpeg

from mosaic.jobs.utils import MOSAIC_TEMP_DIR


class Job:
    info_fname = 'job.json'
    inputs_dirname = 'inputs'
    outputs_dirname = 'outputs'

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
        self._job_dirpath = MOSAIC_TEMP_DIR / f'{self.id}'
        self._input_dirpath = self._job_dirpath / self.inputs_dirname
        self._output_dirpath = self._job_dirpath / self.outputs_dirname

    def create_dirs(self) -> None:
        Path.mkdir(self._input_dirpath, parents=True)
        Path.mkdir(self._output_dirpath, parents=True)

    def start(self) -> None:
        # split video into segments
        ffmpeg.input(
            str(self.input_file),
        ).output(
            str(self._input_dirpath / 'input_%06d.ts'),
            f='segment',
            segment_time=300,
            reset_timestamps=1,
            c='copy'
        ).global_args(
            '-loglevel', 'fatal',
            '-progress', 'pipe:1',
        ).run()

        # process the segments into output segments
        print('processing the segments into output segments')

        # combine the output segments
        print('combining the output segments')
        print(f'finally should produce {self.output_file.name}')

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
        info_fpath = self._job_dirpath / self.info_fname
        info = {k: str(v) for k, v in dict(
            command=self.command,
            id=self.id,
            input_file=self.input_file,
            output_file=self.output_file,
        ).items()}
        with open(info_fpath, 'w') as f:
            json.dump(info, f, indent=4)
