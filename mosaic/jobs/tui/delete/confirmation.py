import shutil
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Label

if TYPE_CHECKING:
    from mosaic.jobs.tui.delete import JobList


class ConfirmationModalScreen(ModalScreen[bool]):
    """A minimal key-driven confirmation modal."""

    from .bindings import confirmatino_model_screen as BINDINGS
    from .styles import confirmation_model_screen as CSS

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
    def __init__(self, job_list: JobList) -> None:
        self.dashboard = job_list.dashboard
        self._list_view = job_list.list_view

    def prompt(self) -> None:
        if self._list_view.highlighted_item is not None:
            self.dashboard.push_screen(ConfirmationModalScreen(), self._delete_job)

    def _delete_job(self, confirmed: bool | None) -> None:
        if not confirmed:
            return

        item = self._list_view.highlighted_item

        if not item:
            self.dashboard.notify(f'Failed to get job info', severity='error')
            return

        job = item.job

        try:
            if job.job_dirpath.exists():
                shutil.rmtree(job.job_dirpath)
            item.remove()
            self.dashboard.notify(f'Job {job.id} deleted.')
        except Exception as e:
            self.dashboard.notify(f'Failed to delete: {e}', severity="error")
