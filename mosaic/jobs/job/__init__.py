import json
from datetime import datetime
from pathlib import Path
from typing import cast
from uuid import UUID, uuid4

from mosaic.jobs.job.base import Job
from mosaic.jobs.job.copy import CopyJob
from mosaic.jobs.job.free import FreeJob
from mosaic.jobs.job.upscale import UpscaleJob
from mosaic.jobs.utils import Command
from mosaic.utils.time import HMS


def load_job(
    dirpath: Path
) -> Job:
    fpath = dirpath / Job.info_fname
    with open(fpath, 'r') as f:
        d = json.load(f)
    command: Command = cast(Command, d['command'])
    id = UUID(d['id'])
    timestamp = datetime.fromisoformat(d['timestamp'])
    segment_time = HMS.from_str(d['segment_time'])
    input_file = Path(d['input_file'])
    duration = float(d['duration'])
    framerate = str(d['framerate'])
    output_file = Path(d['output_file'])
    if command == 'free':
        return FreeJob(
            command=command,
            id=id,
            timestamp=timestamp,
            segment_time=segment_time,
            input_file=input_file,
            duration=duration,
            framerate=framerate,
            output_file=output_file,
        )
    elif command == 'copy':
        return CopyJob(
            command=command,
            id=id,
            timestamp=timestamp,
            segment_time=segment_time,
            input_file=input_file,
            duration=duration,
            framerate=framerate,
            output_file=output_file,
        )
    elif command == 'upscale':
        model = d['model']
        scale = d['scale']
        return UpscaleJob(
            command=command,
            id=id,
            timestamp=timestamp,
            segment_time=segment_time,
            model=model,
            scale=scale,
            input_file=input_file,
            duration=duration,
            framerate=framerate,
            output_file=output_file,
        )
