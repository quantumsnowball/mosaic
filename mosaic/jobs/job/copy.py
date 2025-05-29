import json
import shutil
from typing import override

from mosaic.jobs.job.base import Job
from mosaic.utils.logging import log


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
