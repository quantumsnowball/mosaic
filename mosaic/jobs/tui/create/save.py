from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Label


class SaveAsModalScreen(ModalScreen[str]):
    from .bindings import save as BINDINGS
    from .styles import save as CSS

    def __init__(self, default_path: Path) -> None:
        super().__init__()
        self._default_path = default_path

    def compose(self) -> ComposeResult:
        with Vertical(id="modal-container"):
            yield Label("Create lada job, save output file as:")
            yield Input(
                value=str(self._default_path),
                placeholder="Save output file as ...",
                id="output-input"
            )
            yield Label("Press <Escape> to cancel")

    def on_mount(self) -> None:
        self.query_one(Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        # press enter to proceed
        self.dismiss(event.value)

    def action_cancel(self) -> None:
        # press excape to cancel
        self.dismiss(None)
