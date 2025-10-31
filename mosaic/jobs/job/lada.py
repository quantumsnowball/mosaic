import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Self, override
from uuid import uuid4

import click

from mosaic.jobs.job.base import Job, Save
from mosaic.lada.cleaner import Cleaner
from mosaic.utils import PACKAGE_ROOT
from mosaic.utils.logging import log
from mosaic.utils.spec import VideoSource
from mosaic.utils.time import HMS


@dataclass
class LadaJobSave(Save):
    pass


class LadaJob(Job):
    @override
    def proceed(self) -> None:
        # loop through available tasks
        while task := self.checklist.next_task():
            click.echo(self.progress(task.name))

            with Cleaner(
                input_file=self._input_dirpath / task.name,
                output_file=self._output_dirpath / task.name,
                netD_path=PACKAGE_ROOT / 'lada/net/state_dicts/lada_mosaic_detection_model_v2.pt',
                netR_path=PACKAGE_ROOT / 'lada/net/state_dicts/lada_mosaic_restoration_model_generic_v1.2.pth',
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
        info = LadaJobSave(
            command=self.command,
            id=self.id,
            timestamp=self.timestamp_iso,
            segment_time=self.segment_time,
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
        input_file: Path,
        output_file: Path
    ) -> Self:
        origin = VideoSource(input_file)
        origin.ensure_framerate_is_simplified()
        return cls(
            command='lada',
            id=uuid4(),
            timestamp=datetime.now(),
            segment_time=segment_time,
            input_file=input_file,
            duration=origin.duration,
            framerate=origin.framerate,
            output_file=output_file,
        )
