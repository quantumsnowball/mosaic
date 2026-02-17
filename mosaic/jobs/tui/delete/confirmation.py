import shutil
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Label

from mosaic.jobs.tui.delete.list import JobListView

if TYPE_CHECKING:
    from mosaic.jobs.tui.dashboard import Dashboard


class ConfirmationModalScreen(ModalScreen[bool]):
    """A minimal key-driven confirmation modal."""

    from .bindings import confirmatino_model_screen as BINDINGS
    from .styles import confirmation as CSS

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label(
                "Are you sure? "
                "[bold red]Y[/] to Delete / [bold white]N[/] to Cancel",
            )

    def action_confirm(self) -> None:
        self.dismiss(True)

    def action_cancel(self) -> None:
        self.dismiss(False)


class Confirmation:
    def __init__(self, app: Dashboard, job_list_view: JobListView) -> None:
        self._app = app
        self._job_list_view = job_list_view

    def prompt(self) -> None:
        if self._job_list_view.highlighted_item is not None:
            self._app.push_screen(ConfirmationModalScreen(), self._delete_job)

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
