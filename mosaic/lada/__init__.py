from pathlib import Path

import click

import mosaic.lada.args as args
from mosaic.lada.cleaner import Cleaner
from mosaic.utils.logging import log
from mosaic.utils.path import PathParamType
from mosaic.utils.service import service

PACKAGE_DIR = Path(__file__).parent


@click.command()
@service()
@click.option('-i', '--input-file', required=True, type=PathParamType(), help='input media path')
@click.option('-y', '--force', is_flag=True, default=False, help='overwrite output file without asking')
@click.argument('output-file', required=True, type=PathParamType())
@args.preprocess
def lada(
    input_file: Path,
    output_file: Path,
) -> None:
    # run
    with Cleaner(
        input_file=input_file,
        output_file=output_file,
        netD_path=PACKAGE_DIR / 'net/state_dicts/lada_mosaic_detection_model_v2.pt',
        netR_path=PACKAGE_DIR / 'net/state_dicts/lada_mosaic_restoration_model_generic_v1.2.pth',
    ) as cleaner:
        try:
            cleaner.run()
        except KeyboardInterrupt as e:
            log.info(e.__class__)
            cleaner.stop()
