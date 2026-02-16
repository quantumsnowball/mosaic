from textual.app import ComposeResult
from textual.containers import Center, Middle
from textual.screen import ModalScreen
from textual.widgets import Label


class ConfirmDelete(ModalScreen[bool]):
    """A minimal key-driven confirmation modal."""

    # Key bindings specifically for this modal
    BINDINGS = [
        ("y", "confirm", "Yes, Delete"),
        ("Y", "confirm", "Yes, Delete"),
        ("n", "cancel", "No, Cancel"),
        ("N", "cancel", "No, Cancel"),
        ("escape", "cancel", "Cancel")
    ]

    def compose(self) -> ComposeResult:
        # Wrap in Center/Middle to float it in the screen center
        with Center():
            with Middle():
                yield Label(
                    "Are you sure? [bold red]Y[/] to Delete / [bold white]N[/] to Cancel",
                    id="confirm-msg"
                )

    def action_confirm(self) -> None:
        self.dismiss(True)

    def action_cancel(self) -> None:
        self.dismiss(False)

    CSS = """
    ConfirmDelete {
        align: center middle;
        background: $background 50%; /* Dim the background */
    }
    #confirm-msg {
        padding: 2 4;
        background: $surface;
        border: thick $error;
        width: auto;
    }
    """
