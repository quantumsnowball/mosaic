from pathlib import Path
from typing import Annotated

import typer
from typer import Argument, Option

from mosaic.lada.args import preprocess_args
from mosaic.lada.cleaner import Cleaner
from mosaic.utils.logging import log
from mosaic.utils.service import service

PACKAGE_DIR = Path(__file__).parent


app = typer.Typer()


@app.command(no_args_is_help=True)
@service()
def lada(
    output_file: Annotated[Path, Argument(help="Output file path", show_default=False)],
    input_file: Annotated[Path, Option("--input-file", "-i", help="input media path", show_default=False)],
    force: Annotated[bool, Option("--force", "-y", help="overwrite output file without asking")] = False,
) -> None:
    # preprocess args
    output_file, input_file = preprocess_args(output_file, input_file, force)

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
