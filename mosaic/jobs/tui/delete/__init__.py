from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Vertical

from mosaic.jobs.tui.delete.confirmation import Confirmation
from mosaic.jobs.tui.delete.list import JobListView

if TYPE_CHECKING:
    from mosaic.jobs.tui.dashboard import Dashboard


class JobList(Vertical):
    def __init__(self, app: Dashboard) -> None:
        super().__init__(classes='section')
        self._app = app
        self.list_view = JobListView(id='job_list')
        self.confirmation = Confirmation(app, self.list_view)

    def compose(self) -> ComposeResult:
        yield self.list_view
