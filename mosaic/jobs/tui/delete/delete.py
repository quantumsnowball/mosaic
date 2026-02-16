import shutil
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Center, Middle
from textual.screen import ModalScreen
from textual.widgets import Label

from mosaic.jobs.tui.delete.list import JobListView

if TYPE_CHECKING:
    from mosaic.jobs.tui.dashboard import Dashboard


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


class Confirmation:
    def __init__(self, app: Dashboard, job_list_view: JobListView) -> None:
        self._app = app
        self._job_list_view = job_list_view

    def prompt(self) -> None:
        if self._job_list_view.highlighted_item is not None:
            self._app.push_screen(ConfirmDelete(), self._delete_job)

    def _delete_job(self, confirmed: bool | None) -> None:
        if not confirmed:
            return

        item = self._job_list_view.highlighted_item

        if not item:
            self._app.notify(f'Failed to get job info', severity='error')
            return

        job = item.job

        try:
            if job.job_dirpath.exists():
                shutil.rmtree(job.job_dirpath)
            item.remove()
            self._app.notify(f'Job {job.id} deleted.')
        except Exception as e:
            self._app.notify(f'Failed to delete: {e}', severity="error")
