import json
from datetime import datetime
from pathlib import Path
from typing import Self
from uuid import UUID, uuid4

from mosaic.free import cleaner
from mosaic.free.net.netG import video
from mosaic.free.net.netM import bisenet
from mosaic.jobs.job.checklist import Checklist
from mosaic.jobs.utils import JOBS_DIR
from mosaic.utils import PACKAGE_ROOT
from mosaic.utils.ffmpeg import FFmpeg
from mosaic.utils.progress import ProgressBar
from mosaic.utils.spec import VideoSource


class Job:
    info_fname = 'job.json'
    inputs_dirname = 'inputs'
    outputs_dirname = 'outputs'
    outputs_list_fname = 'outputs.txt'
    checklist_fname = 'checklist.db'
    concat_index_fname = 'concat.txt'
    segment_time = '00:05:00'
    segment_ext = 'mp4'
    segment_pattern = f'%06d.{segment_ext}'

    def __init__(
        self,
        *,
        command: str,
        id: UUID,
        timestamp: datetime,
        input_file: Path,
        output_file: Path,
    ) -> None:
        self.command = command
        self.id = id
        self.timestamp = timestamp
        self.timestamp_iso = self.timestamp.isoformat()
        self.timestamp_pp = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        self.input_file = input_file
        self.output_file = output_file
        self.origin = VideoSource(self.input_file)
        self._job_dirpath = JOBS_DIR / f'{self.timestamp_iso.replace(':', '.').replace('T', '_')}'
        self._input_dirpath = self._job_dirpath / self.inputs_dirname
        self._output_dirpath = self._job_dirpath / self.outputs_dirname
        self._checklist_fpath = self._job_dirpath / self.checklist_fname
        self.checklist = Checklist(self._checklist_fpath)

    def __enter__(self) -> Self:
        Path.mkdir(self._job_dirpath, parents=True)
        Path.mkdir(self._input_dirpath)
        Path.mkdir(self._output_dirpath)
        return self

    def __exit__(self, *_) -> None:
        pass

    def initialize(self) -> None:
        # split video into segments
        with ProgressBar(self.origin.duration) as pbar:
            FFmpeg(
            ).global_args(
                '-loglevel', 'fatal',
                '-progress', str(pbar.input),
                '-stats_period', ProgressBar.REFRESH_RATE,
            ).input(
                '-i', str(self.input_file),
            ).output(
                '-f', 'segment',
                '-segment_time', self.segment_time,
                '-vcodec', 'libx264',
                '-acodec', 'copy',
                str(self._input_dirpath / self.segment_pattern),
            ).run()

        # create a sqlite db as the checklist
        self.checklist.create()
        self.checklist.initialize(self._input_dirpath, ext=self.segment_ext, val=False)

    def proceed(self) -> None:
        # loop through available tasks
        while task := self.checklist.next_task():
            # process task with the correct command
            if self.command == 'free':
                cleaner.run(
                    input_file=self._input_dirpath / task.name,
                    start_time=None,
                    end_time=None,
                    output_file=self._output_dirpath / task.name,
                    raw_info=False,
                    netM=bisenet(PACKAGE_ROOT/'free/net/netM/state_dicts/mosaic_position.pth'),
                    netG=video(PACKAGE_ROOT/'free/net/netG/state_dicts/clean_youknow_video.pth'),
                )
                # mark task done
                self.checklist.mark_done(task)

    def finalize(self) -> None:
        # create concat index
        index = self._output_dirpath / self.concat_index_fname
        parts = [p for p in sorted(self._output_dirpath.glob(f'*.{self.segment_ext}'))]
        with open(index, 'w') as f:
            for part in parts:
                f.write(f'file {part.name}\n')
        # combine the output segments
        FFmpeg(
        ).global_args(
            '-y',
        ).input(
            '-f', 'concat',
            '-i', str(index),
        ).output(
            '-c', 'copy',
            str(self.output_file),
        ).run()

    def run(self) -> None:
        if not self._checklist_fpath.exists():
            self.initialize()
        if not self.checklist.is_finished:
            self.proceed()
        if self.checklist.is_finished:
            self.finalize()

    def save(self) -> None:
        info_fpath = self._job_dirpath / self.info_fname
        info = {k: str(v) for k, v in dict(
            command=self.command,
            id=self.id,
            timestamp=self.timestamp_iso,
            input_file=self.input_file,
            output_file=self.output_file,
        ).items()}
        with open(info_fpath, 'w') as f:
            json.dump(info, f, indent=4)

    @classmethod
    def load(cls, dirpath: Path) -> Self:
        fpath = dirpath / cls.info_fname
        with open(fpath, 'r') as f:
            d = json.load(f)
        return cls(
            command=d['command'],
            id=UUID(d['id']),
            timestamp=datetime.fromisoformat(d['timestamp']),
            input_file=Path(d['input_file']),
            output_file=Path(d['output_file']),
        )

    @classmethod
    def create(cls, *, command: str, input_file: Path, output_file: Path) -> Self:
        job = cls(
            command=command,
            id=uuid4(),
            timestamp=datetime.now(),
            input_file=input_file,
            output_file=output_file,
        )
        return job
