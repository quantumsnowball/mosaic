import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Self, override
from uuid import UUID, uuid4

import click

from mosaic.jobs.job.base import Job, Save
from mosaic.jobs.utils import Command
from mosaic.upscale.net import presets
from mosaic.upscale.net.real_esrgan import RealESRGANer
from mosaic.upscale.upscaler import Upscaler
from mosaic.utils.logging import log
from mosaic.utils.spec import VideoSource
from mosaic.utils.time import HMS


@dataclass
class UpscaleJobSave(Save):
    scale: str
    model: str


class UpscaleJob(Job):
    def __init__(
        self,
        *,
        command: Command,
        id: UUID,
        timestamp: datetime,
        segment_time: HMS,
        model: str,
        scale: str,
        input_file: Path,
        duration: float,
        framerate: str,
        output_file: Path,
    ) -> None:
        super().__init__(
            command=command,
            id=id,
            timestamp=timestamp,
            segment_time=segment_time,
            input_file=input_file,
            duration=duration,
            framerate=framerate,
            output_file=output_file,
        )
        self.scale = scale
        self.model = model

    @override
    def proceed(self) -> None:
        # loop through available tasks
        while task := self.checklist.next_task():
            click.echo(self.progress(task.name))

            # load upsampler
            net = presets[self.model]
            upsampler = RealESRGANer(
                scale=net.scale,
                model_path=net.model_path,
                model=net.model,
                gpu_id=0,
            )

            with Upscaler(
                input_file=self._input_dirpath / task.name,
                start_time=None,
                end_time=None,
                output_file=self._output_dirpath / task.name,
                raw_info=False,
                scale=self.scale,
                upsampler=upsampler,
            ) as cleaner:
                try:
                    cleaner.run()
                except KeyboardInterrupt as e:
                    log.info(e.__class__)
                    cleaner.stop()
                    break

            # mark task done
            self.checklist.mark_done(task)

    @override
    def save(self) -> None:
        info_fpath = self.job_dirpath / self.info_fname
        info = UpscaleJobSave(
            command=self.command,
            id=self.id,
            timestamp=self.timestamp_iso,
            segment_time=self.segment_time,
            scale=self.scale,
            model=self.model,
            input_file=self.input_file,
            duration=self.duration,
            framerate=self.framerate,
            output_file=self.output_file,
        ).dict
        with open(info_fpath, 'w') as f:
            json.dump(info, f, indent=4)

    @classmethod
    def create(
        cls,
        *,
        segment_time: HMS,
        model: str,
        scale: str,
        input_file: Path,
        output_file: Path
    ) -> Self:
        origin = VideoSource(input_file)
        origin.ensure_framerate_is_simplified()
        return cls(
            command='upscale',
            id=uuid4(),
            timestamp=datetime.now(),
            segment_time=segment_time,
            model=model,
            scale=scale,
            input_file=input_file,
            duration=origin.duration,
            framerate=origin.framerate,
            output_file=output_file,
        )
