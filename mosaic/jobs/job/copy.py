import json
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Self, override
from uuid import uuid4

from mosaic.jobs.job.base import Job, Save
from mosaic.utils.logging import log
from mosaic.utils.spec import VideoSource
from mosaic.utils.time import HMS


@dataclass
class CopyJobSave(Save):
    pass


class CopyJob(Job):
    @override
    def proceed(self) -> None:
        # loop through available tasks
        while task := self.checklist.next_task():
            # no processing just copy for testing purpose
            try:
                shutil.copy(
                    self._input_dirpath / task.name,
                    self._output_dirpath / task.name,
                )
            except KeyboardInterrupt as e:
                log.info(e.__class__)
                break

            # mark task done
            self.checklist.mark_done(task)

    @override
    def save(self) -> None:
        info_fpath = self.job_dirpath / self.info_fname
        info = CopyJobSave(
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
            command='copy',
            id=uuid4(),
            timestamp=datetime.now(),
            segment_time=segment_time,
            input_file=input_file,
            duration=origin.duration,
            framerate=origin.framerate,
            output_file=output_file,
        )
