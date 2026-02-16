import shutil
from typing import TYPE_CHECKING

from mosaic.jobs.tui.delete.delete import Confirmation, ConfirmDelete
from mosaic.jobs.tui.delete.list import JobListItem, JobListView

if TYPE_CHECKING:
    from mosaic.jobs.tui.dashboard import Dashboard


class JobList:
    id = 'job_list'

    def __init__(self, app: Dashboard) -> None:
        self._app = app
        self.job_list_view = JobListView(id=self.id)
        self.confirmation = Confirmation(app, self.job_list_view)

    async def populate_job_list(self) -> None:
        self.job_list_view.clear()
        await self.job_list_view.fetch_jobs()
        self.job_list_view.select_first_item()

    def prompt_for_delete_confirmation(self) -> None:
        self.confirmation.prompt()
