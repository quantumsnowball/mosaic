from typing import TYPE_CHECKING

from mosaic.jobs.tui.delete.delete import Confirmation
from mosaic.jobs.tui.delete.list import JobListView

if TYPE_CHECKING:
    from mosaic.jobs.tui.dashboard import Dashboard


class JobList:
    id = 'job_list'

    def __init__(self, app: Dashboard) -> None:
        self._app = app
        self.list_view = JobListView(id=self.id)
        self.confirmation = Confirmation(app, self.list_view)
