import shutil
from typing import TYPE_CHECKING

from textual.widgets import ListView

from mosaic.jobs.tui.delete.delete import ConfirmDelete
from mosaic.jobs.tui.delete.list import JobListItem

if TYPE_CHECKING:
    from mosaic.jobs.tui.dashboard import Dashboard


class JobHandler:
    def __init__(self, app: Dashboard) -> None:
        self._app = app

    def prompt_for_delete_confirmation(self) -> None:
        item = self._app.query_one("#job_list", ListView).highlighted_child
        if isinstance(item, JobListItem):
            self._app.push_screen(ConfirmDelete(), self._delete_job)

    def _delete_job(self, confirmed: bool | None) -> None:
        if not confirmed:
            return

        item = self._app.query_one("#job_list", ListView).highlighted_child

        if not isinstance(item, JobListItem):
            self._app.notify(f'Failed to get job info', severity='error')
            return

        job = item.job

        try:
            if job.job_dirpath.exists():
                shutil.rmtree(job.job_dirpath)
            item.remove()
            self._app.notify(f"Job {job.id} deleted.")
        except Exception as e:
            self._app.notify(f"Failed to delete: {e}", severity="error")
