import os
import uuid
from pathlib import Path
from threading import Thread
from typing import Self

from alive_progress import alive_bar


class ProgressBar:
    def __init__(self, duration: float) -> None:
        self.duration = duration
        self._pipe = Path(f'/tmp/{__name__}.{uuid.uuid4()}')
        self._thread: Thread | None = None

    @property
    def input(self) -> Path:
        return self._pipe

    @property
    def thread(self) -> Thread | None:
        return self._thread

    def start(self) -> Self:
        if not self._pipe.exists():
            os.mkfifo(self._pipe)
        return self

    def stop(self) -> None:
        if self._pipe.exists():
            self._pipe.unlink()

    def wait(self) -> None:
        if self._thread:
            self._thread.join()

    def run(self) -> None:
        def worker() -> None:
            with (
                alive_bar(manual=True) as bar,
                open(self.input, 'r') as progress,
            ):
                pct = 0.0
                speed_text = ''
                fps_text = ''

                def info() -> str:
                    return f'{speed_text}, {fps_text}'

                while line := progress.readline():
                    # break gracefully even before EOF
                    if line.startswith('progress=end'):
                        break

                    line = line.strip()
                    # track speed
                    if line.startswith('speed='):
                        speed_text = line
                        bar.text(info())
                    # track fps
                    elif line.startswith('fps='):
                        fps_text = line
                        bar.text(info())
                    # calc current time
                    elif line.startswith('out_time_us='):
                        out_time_us_text = line.split('=', maxsplit=1)[1]
                        try:
                            out_time = float(out_time_us_text) / 1e+6
                        except ValueError:
                            continue
                        # calc and show progress percentage
                        pct = out_time / self.duration
                        bar(min(pct, 1.0))

                # finish bar to 100%
                bar(1.0)

        # run in own thread
        self._thread = Thread(target=worker)
        self._thread.start()
