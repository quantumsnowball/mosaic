from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Vertical

from mosaic.jobs.tui.delete.confirmation import Confirmation
from mosaic.jobs.tui.delete.list import JobListView

if TYPE_CHECKING:
    from mosaic.jobs.tui import Main


class JobList(Vertical):
    def __init__(self, main: Main) -> None:
        super().__init__(classes='section')
        self.main = main
        self.border_title = 'Jobs'
        self.border_subtitle = 'Jobs'
        self.list_view = JobListView()
        self.confirmation = Confirmation(self)

    def compose(self) -> ComposeResult:
        yield self.list_view
