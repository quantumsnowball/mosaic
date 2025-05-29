import json
from datetime import datetime
from pathlib import Path
from typing import override
from uuid import UUID

from mosaic.jobs.job.base import Job
from mosaic.jobs.utils import Command
from mosaic.upscale.net import presets
from mosaic.upscale.net.real_esrgan import RealESRGANer
from mosaic.upscale.upscaler import Upscaler
from mosaic.utils.logging import log
from mosaic.utils.time import HMS


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
        output_file: Path,
    ) -> None:
        super().__init__(
            command=command,
            id=id,
            timestamp=timestamp,
            segment_time=segment_time,
            input_file=input_file,
            output_file=output_file,
        )
        self.scale = scale
        self.model = model

    @override
    def proceed(self) -> None:
        # loop through available tasks
        while task := self.checklist.next_task():
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
        info = {k: str(v) for k, v in dict(
            command=self.command,
            id=self.id,
            timestamp=self.timestamp_iso,
            segment_time=self.segment_time,
            scale=self.scale,
            model=self.model,
            input_file=self.input_file,
            output_file=self.output_file,
        ).items()}
        with open(info_fpath, 'w') as f:
            json.dump(info, f, indent=4)
