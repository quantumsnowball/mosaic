from textual.app import ComposeResult
from textual.widgets import Label, ListItem

from mosaic.jobs.job.base import Job
from mosaic.jobs.text import job_info


class JobListItem(ListItem):
    def __init__(self, job: Job) -> None:
        super().__init__()
        self.job = job
        self.job_info = job_info(job, verbose=True, textual_color=True)

    def compose(self) -> ComposeResult:
        yield Label(self.job_info)
