import os
import signal
import subprocess
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

import click

from mosaic.utils import HMS

TEMP_DIRNAME = '.temp'


@dataclass
class DeepMosaicsCommand:
    root: Path
    media_path: Path
    result_dir: Path
    model_path: Path | None
    start_time: HMS | None
    end_time: HMS | None
    preview: bool

    def __post_init__(self) -> None:
        self.default_model_path = self.root/'DeepMosaics'/'pretrained_models'/'clean_youknow_video.pth'
        self.model_path = self.model_path if self.model_path is not None else self.default_model_path

    @property
    def tokens(self) -> list[str]:
        parts = []
        deepmosaic_path = self.root / 'DeepMosaics' / 'deepmosaic.py'
        parts += ['python', str(deepmosaic_path)]
        parts += ['--mode', 'clean']
        if not self.preview:
            parts += ['--no_preview']
        parts += ['--media_path', str(self.media_path)]
        if self.start_time and self.end_time:
            if not self.end_time > self.start_time:
                raise ValueError('Invalid start time or end time')
            last_time = str(self.end_time - self.start_time)
            parts += ['--start_time', str(self.start_time)]
            parts += ['--last_time', str(last_time)]
        parts += ['--result_dir', str(self.result_dir)]
        parts += ['--model_path', str(self.model_path)]
        parts += ['--temp_dir', str(self.result_dir/TEMP_DIRNAME)]

        return parts

    @property
    def result_file(self) -> Path:
        return self.result_dir / f'{self.media_path.stem}_clean.mp4'

    def pprint(self) -> None:
        click.echo(str(self).replace('--', '\n--'))

    def __str__(self) -> str:
        return ' '.join(self.tokens)

    def run(self) -> None:
        # run in process group
        proc = subprocess.Popen(self.tokens, preexec_fn=os.setsid)
        try:
            proc.wait()
        except KeyboardInterrupt:
            os.killpg(proc.pid, signal.SIGTERM)
