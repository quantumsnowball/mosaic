from textual.app import ComposeResult
from textual.widgets import Label, ListItem, ListView

from mosaic.jobs.job.base import Job
from mosaic.jobs.manager import Manager
from mosaic.jobs.text import job_info


class JobListItem(ListItem):
    def __init__(self, job: Job) -> None:
        super().__init__()
        self.job = job
        self.job_info = job_info(job, verbose=True, textual_color=True)

    def compose(self) -> ComposeResult:
        yield Label(self.job_info)


class JobListView(ListView):
    from .bindings import list_view as BINDINGS

    def __init__(self, id: str) -> None:
        super().__init__(id=id)

    @property
    def highlighted_item(self) -> JobListItem | None:
        item = self.highlighted_child
        return item if isinstance(item, JobListItem) else None

    async def populate(self) -> None:
        self.clear()
        with Manager() as manager:
            for job in manager.jobs:
                await self.append(JobListItem(job))
        if len(self) > 0:
            self.index = 0
