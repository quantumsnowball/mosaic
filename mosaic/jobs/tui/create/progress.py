from threading import Thread
from typing import TYPE_CHECKING, Self

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Label, ProgressBar

import mosaic.utils.progress

if TYPE_CHECKING:
    from mosaic.jobs.tui import Main


class ProgressBarModalScreen(ModalScreen):
    from .bindings import progress_bar_model_screen as BINDINGS
    from .styles import progress_bar_model_screen as CSS

    def __init__(self) -> None:
        super().__init__()
        self.progress = ProgressBar(total=100, show_eta=False)

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("Processing Job...")
            yield self.progress
            yield Label("Preparing...")

    def action_cancel(self) -> None:
        self.dismiss(None)


class CreateJobProgressBar(mosaic.utils.progress.ProgressBar):
    main: Main

    @classmethod
    def bind(cls, main: Main) -> type[Self]:
        cls.main = main
        return cls

    def __init__(self, duration: float) -> None:
        super().__init__(duration)
        self._screen = ProgressBarModalScreen()
        self._bar = self._screen.progress

    def __enter__(self) -> Self:
        # push screen
        self.main.call_from_thread(self.main.push_screen, self._screen)
        return super().__enter__()

    def __exit__(self, type, value, traceback) -> None:
        # dismiss screen
        self.main.call_from_thread(self._screen.dismiss)
        return super().__exit__(type, value, traceback)

    def run(self) -> None:
        def worker() -> None:
            with (
                open(self.input, 'r') as progress,
            ):
                pct = 0.0
                speed_text = ''
                fps_text = ''

                while line := progress.readline():
                    # break gracefully even before EOF
                    if line.startswith('progress=end'):
                        # finish bar to 100% then break loop
                        self.main.call_from_thread(self._bar.update, progress=1.0, total=1.0)
                        break

                    line = line.strip()
                    # calc current time
                    if line.startswith('out_time_us='):
                        out_time_us_text = line.split('=', maxsplit=1)[1]
                        try:
                            out_time = float(out_time_us_text) / 1e+6
                        except ValueError:
                            continue
                        # calc and show progress percentage
                        pct = min(out_time / self.duration, 1.0)
                        self.main.call_from_thread(self._bar.update, progress=pct, total=1.0)

        # run in own thread
        self._thread = Thread(target=worker)
        self._thread.start()
