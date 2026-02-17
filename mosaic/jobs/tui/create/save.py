from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label


class OutputPathModal(ModalScreen[str]):
    """A modal to get the output path from the user."""

    def __init__(self, default_path: str) -> None:
        super().__init__()
        self.default_path = default_path

    def compose(self) -> ComposeResult:
        with Vertical(id="modal-container"):
            yield Label("Confirm Output Path:")
            yield Input(
                value=self.default_path,
                placeholder="Enter path...",
                id="output-input"
            )
            with Horizontal(id="modal-buttons"):
                yield Button("Cancel", variant="primary", id="cancel")
                yield Button("Create Job", variant="success", id="create")

    def on_mount(self) -> None:
        # Auto-focus the input so the user can start typing immediately
        self.query_one(Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "create":
            self.dismiss(self.query_one(Input).value)
        else:
            self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Allows pressing 'Enter' inside the input to submit."""
        self.dismiss(event.value)

    CSS = """
    OutputPathModal {
        align: center middle;
        background: $background 50%;
    }
    #modal-container {
        width: 60;
        height: auto;
        padding: 1 2;
        background: $surface;
        border: thick $primary;
    }
    #output-input {
        margin: 1 0;
    }
    #modal-buttons {
        height: auto;
        align: right middle;
    }
    #modal-buttons Button {
        margin-left: 1;
    }
    """
