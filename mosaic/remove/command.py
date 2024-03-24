from dataclasses import dataclass
from pathlib import Path

import click

from mosaic.utils import HMS


@dataclass
class DeepMosaicsCommand:
    root: Path
    media_path: str
    result_dir: str
    model_path: str | None
    start_time: HMS | None
    end_time: HMS | None
    preview: bool

    def __post_init__(self) -> None:
        self.default_model_path = str(self.root/'DeepMosaics'/'pretrained_models'/'clean_youknow_video.pth')
        self.model_path = self.model_path if self.model_path is not None else self.default_model_path

    @property
    def tokens(self) -> list[str]:
        parts = []
        deepmosaic_path = str(self.root / 'DeepMosaics' / 'deepmosaic.py')
        parts += ['python', deepmosaic_path]
        parts += ['--mode', 'clean']
        if not self.preview:
            parts += ['--no_preview']
        parts += ['--media_path', self.media_path]
        if self.start_time and self.end_time:
            if not self.end_time > self.start_time:
                raise ValueError('Invalid start time or end time')
            last_time = str(self.end_time - self.start_time)
            parts += ['--start_time', str(self.start_time)]
            parts += ['--last_time', str(last_time)]
        parts += ['--result_dir', self.result_dir]
        parts += ['--model_path', self.model_path]

        return parts

    def pprint(self) -> None:
        click.echo(str(self).replace('--', '\n--'))

    def __str__(self) -> str:
        return ' '.join(self.tokens)
