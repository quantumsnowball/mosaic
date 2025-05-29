import json
from datetime import datetime
from pathlib import Path
from typing import Self, override
from uuid import uuid4

import click

from mosaic.free.cleaner import Cleaner
from mosaic.free.net.netG import video
from mosaic.free.net.netM import bisenet
from mosaic.jobs.job.base import Job
from mosaic.utils import PACKAGE_ROOT
from mosaic.utils.logging import log
from mosaic.utils.time import HMS


class FreeJob(Job):
    @override
    def proceed(self) -> None:
        # loop through available tasks
        while task := self.checklist.next_task():
            click.echo(self.progress(task.name))

            with Cleaner(
                input_file=self._input_dirpath / task.name,
                start_time=None,
                end_time=None,
                output_file=self._output_dirpath / task.name,
                raw_info=False,
                netM=bisenet(PACKAGE_ROOT/'free/net/netM/state_dicts/mosaic_position.pth'),
                netG=video(PACKAGE_ROOT/'free/net/netG/state_dicts/clean_youknow_video.pth'),
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
            input_file=self.input_file,
            output_file=self.output_file,
        ).items()}
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
        return cls(
            command='free',
            id=uuid4(),
            timestamp=datetime.now(),
            segment_time=segment_time,
            input_file=input_file,
            output_file=output_file,
        )
