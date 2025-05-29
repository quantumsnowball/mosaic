import json
from typing import override

from mosaic.jobs.job.base import Job
from mosaic.upscale.net import presets
from mosaic.upscale.net.real_esrgan import RealESRGANer
from mosaic.upscale.upscaler import Upscaler
from mosaic.utils.logging import log


class UpscaleJob(Job):
    @override
    def proceed(self) -> None:
        # loop through available tasks
        while task := self.checklist.next_task():
            # load upsampler
            net = presets[model]
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
                scale=scale,
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
            input_file=self.input_file,
            output_file=self.output_file,
        ).items()}
        with open(info_fpath, 'w') as f:
            json.dump(info, f, indent=4)
