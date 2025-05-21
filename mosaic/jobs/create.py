import json
import uuid
from pathlib import Path

import click

from mosaic.jobs.utils import MOSAIC_TEMP_DIR
from mosaic.utils import VideoPathParamType


@click.group
def create() -> None:
    pass


@create.command
@click.option('-i', '--input-file', required=True, type=VideoPathParamType(), help='input media path')
@click.argument('output-file', required=True, type=VideoPathParamType())
def free(
    input_file: Path,
    output_file: Path,
) -> None:
    # create a new job directory
    job_id = uuid.uuid4()
    job_dirname = f'{job_id}'
    job_dirpath = MOSAIC_TEMP_DIR / job_dirname
    Path.mkdir(job_dirpath, parents=True)

    # create the meta data json file
    info_fname = 'job.json'
    info_fpath = job_dirpath / info_fname
    info = {k: str(v) for k, v in dict(
        command='free',
        id=job_id,
        input_file=input_file,
        output_file=output_file,
    ).items()}
    with open(info_fpath, 'w') as f:
        json.dump(info, f, indent=4)
