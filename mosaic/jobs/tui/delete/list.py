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
    def __init__(self, id: str) -> None:
        super().__init__(id=id)

    async def fetch_jobs(self) -> None:
        with Manager() as manager:
            for job in manager.jobs:
                await self.append(JobListItem(job))

    def select_first_item(self) -> None:
        if len(self) > 0:
            self.index = 0
