import shutil
from typing import TYPE_CHECKING

from mosaic.jobs.tui.delete.delete import ConfirmDelete
from mosaic.jobs.tui.delete.list import JobListItem, JobListView

if TYPE_CHECKING:
    from mosaic.jobs.tui.dashboard import Dashboard


class JobList:
    id = 'job_list'

    def __init__(self, app: Dashboard) -> None:
        self._app = app
        self.job_list_view = JobListView(id=self.id)

    async def populate_job_list(self) -> None:
        self.job_list_view.clear()
        await self.job_list_view.fetch_jobs()
        self.job_list_view.select_first_item()

    def prompt_for_delete_confirmation(self) -> None:
        item = self.job_list_view.highlighted_child
        if isinstance(item, JobListItem):
            self._app.push_screen(ConfirmDelete(), self._delete_job)

    def _delete_job(self, confirmed: bool | None) -> None:
        if not confirmed:
            return

        item = self.job_list_view.highlighted_child

        if not isinstance(item, JobListItem):
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
