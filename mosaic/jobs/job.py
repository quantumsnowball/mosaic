import json
from pathlib import Path
from typing import Self
from uuid import UUID, uuid4

import ffmpeg

from mosaic.jobs.utils import MOSAIC_TEMP_DIR
from mosaic.utils.progress import ProgressBar
from mosaic.utils.spec import VideoSource


class Job:
    info_fname = 'job.json'
    inputs_dirname = 'inputs'
    outputs_dirname = 'outputs'
    outputs_list_fname = 'outputs.txt'

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
        self.origin = VideoSource(self.input_file)
        self._job_dirpath = MOSAIC_TEMP_DIR / f'{self.id}'
        self._input_dirpath = self._job_dirpath / self.inputs_dirname
        self._output_dirpath = self._job_dirpath / self.outputs_dirname

    def initialize(self) -> None:
        # create the inputs and outputs dirs
        Path.mkdir(self._input_dirpath, parents=True)
        Path.mkdir(self._output_dirpath, parents=True)

        # split video into segments
        with ProgressBar(self.origin.duration) as pbar:
            ffmpeg.input(
                str(self.input_file),
            ).output(
                str(self._input_dirpath / 'input_%06d.ts'),
                f='segment',
                segment_time=300,
                c='copy'
            ).global_args(
                '-loglevel', 'fatal',
                '-progress', pbar.input,
                '-stats_period', '0.5',
            ).run()

        # TODO: create a sqlite db as the checklist

    def run(self) -> None:
        # TODO: process the segments into output segments
        import shutil
        for f in self._input_dirpath.glob('*.ts'):
            shutil.move(f, self._output_dirpath / f.name)

        # combine the output segments
        outputs = [str(p) for p in sorted(self._output_dirpath.glob('*.ts'))]
        ffmpeg.input(
            f'concat:{"|".join(outputs)}'
        ).output(
            str(self.output_file),
            c='copy'
        ).run()

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
