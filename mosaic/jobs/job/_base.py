from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Self
from uuid import UUID

from mosaic.jobs.job.checklist import Checklist
from mosaic.jobs.job.utils import prompt_overwrite_output
from mosaic.jobs.utils import JOBS_DIR, Command
from mosaic.utils.ffmpeg import FFmpeg
from mosaic.utils.logging import log
from mosaic.utils.progress import ProgressBar
from mosaic.utils.time import HMS


@dataclass
class Save:
    command: str
    id: UUID
    timestamp: str
    segment_time: HMS
    input_file: Path
    width: int
    height: int
    duration: float
    framerate: str
    sar: str
    dar: str
    output_file: Path

    @property
    def dict(self) -> dict[str, str]:
        return {k: str(v) for k, v in asdict(self).items()}


class Job(ABC):
    timescale = '90000'
    info_fname = 'job.json'
    inputs_dirname = 'inputs'
    outputs_dirname = 'outputs'
    outputs_list_fname = 'outputs.txt'
    checklist_fname = 'checklist.db'
    concat_index_fname = 'concat.txt'
    segment_ext = 'mp4'
    segment_pattern = f'%06d.{segment_ext}'

    def __init__(
        self,
        *,
        command: Command,
        id: UUID,
        timestamp: datetime,
        segment_time: HMS,
        input_file: Path,
        width: int,
        height: int,
        duration: float,
        framerate: str,
        sar: str,
        dar: str,
        output_file: Path,
    ) -> None:
        self.command = command
        self.id = id
        self.timestamp = timestamp
        self.timestamp_iso = self.timestamp.isoformat()
        self.timestamp_pp = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        self.segment_time = segment_time
        self.input_file = input_file
        self.output_file = output_file
        self.width = width
        self.height = height
        self.duration = duration
        self.framerate = framerate
        self.sar = sar
        self.dar = dar
        self.aspect = dar if dar != 'n.a.' else f'{width}:{height}'
        self.job_dirpath = JOBS_DIR / f'{self.timestamp_iso.replace(':', '.').replace('T', '_')}'
        self._input_dirpath = self.job_dirpath / self.inputs_dirname
        self._output_dirpath = self.job_dirpath / self.outputs_dirname
        self._checklist_fpath = self.job_dirpath / self.checklist_fname
        self.checklist = Checklist(self._checklist_fpath)

    def __enter__(self) -> Self:
        Path.mkdir(self.job_dirpath, parents=True)
        Path.mkdir(self._input_dirpath)
        Path.mkdir(self._output_dirpath)
        return self

    def __exit__(self, *_) -> None:
        pass

    @property
    def is_finished(self) -> bool:
        return all((
            self.checklist.is_finished,
            self.output_file.exists(),
        ))

    def initialize(self, *, progress_bar_cls: type[ProgressBar] = ProgressBar) -> None:
        with NamedTemporaryFile(suffix='.mp4', dir=self.job_dirpath) as prep_video:
            log.debug(f'prep_video={prep_video.name}')
            # conver video timescale to most universal timescale
            with progress_bar_cls(
                self.duration,
                title='Converting video to universal timescale ...',
            ) as pbar:
                FFmpeg(
                ).global_args(
                    '-loglevel', 'fatal',
                    '-progress', pbar.input,
                    '-stats_period', ProgressBar.REFRESH_RATE,
                    '-y',
                ).input(
                    '-i', self.input_file,
                ).output(
                    '-vcodec', 'copy',
                    '-acodec', 'copy',
                    '-video_track_timescale', self.timescale,
                    prep_video.name
                ).run()

            # split video into segments
            with progress_bar_cls(
                self.duration,
                title='Spliting video into segments ...'
            ) as pbar:
                FFmpeg(
                ).global_args(
                    '-loglevel', 'fatal',
                    '-progress', pbar.input,
                    '-stats_period', ProgressBar.REFRESH_RATE,
                ).input(
                    '-i', prep_video.name,
                ).output(
                    '-f', 'segment',
                    '-segment_time', self.segment_time,
                    '-vcodec', 'copy',
                    '-acodec', 'copy',
                    '-reset_timestamps', '1',
                    self._input_dirpath / self.segment_pattern,
                ).run()

        # create a sqlite db as the checklist
        self.checklist.create()
        self.checklist.initialize(self._input_dirpath, ext=self.segment_ext, val=False)

    @abstractmethod
    def proceed(self) -> None: ...

    def finalize(self) -> None:
        # create concat index
        index = self._output_dirpath / self.concat_index_fname
        parts = [p for p in sorted(self._output_dirpath.glob(f'*.{self.segment_ext}'))]
        with open(index, 'w') as f:
            for part in parts:
                f.write(f'file {part.name}\n')
        # combine the output segments
        with ProgressBar(self.duration) as pbar:
            FFmpeg(
            ).global_args(
                '-y',
                '-loglevel', 'fatal',
                '-progress', pbar.input,
                '-stats_period', ProgressBar.REFRESH_RATE,
            ).input(
                '-f', 'concat',
                '-i', index,
            ).output(
                '-vcodec', 'copy',
                '-acodec', 'copy',
                '-aspect', self.aspect,
                self.output_file,
            ).run()

    def run(self, *, force_overwrite=False) -> None:
        if not force_overwrite and not prompt_overwrite_output(self.output_file):
            return
        if not self._checklist_fpath.exists():
            self.initialize()
        if not self.checklist.is_finished:
            self.proceed()
        if self.checklist.is_finished:
            self.finalize()

    @abstractmethod
    def save(self) -> None: ...

    def progress(self, name: str) -> str:
        done = self.checklist.count_finished
        total = self.checklist.count
        pct = (done + 0.5) / total
        return (
            '\n' +
            f'{name}  ' +
            f'[red]{pct:.2%}[/]' + ', ' +
            f'[yellow]{done+1} / {total}[/] ' + 'on going, ' +
            f'[yellow]{self.segment_time}[/] ' + 'long'
        )
