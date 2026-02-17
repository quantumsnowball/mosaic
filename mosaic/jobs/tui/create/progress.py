from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Label, ProgressBar


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
