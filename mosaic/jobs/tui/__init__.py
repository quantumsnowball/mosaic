from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Footer, Header, Label, ListItem, ListView

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


class Dashboard(App):
    """A simple Textual TUI for managing jobs."""
    CSS = """
    #main-window {
        border: round $primary;      /* The window frame */
        border-title-align: center;  /* Center the title */
        margin: 1 2;                 /* Breathing room from screen edges */
        background: $surface;
    }
    
    #job_list {
        background: transparent;
    }

    #job_list > ListItem.-highlight {
        /* a very faint background */
        background: $accent 25%;
    }


    """

    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        # header
        yield Header()

        # Create a Vertical container to be the main window frame
        with Vertical(id='main-window') as v:
            v.border_title = 'JOBS'
            yield ListView(id='job_list')

        # footer
        yield Footer()

    async def on_mount(self) -> None:
        # Populate the list after the UI has started
        job_list = self.query_one("#job_list", ListView)
        with Manager() as manager:
            for job in manager.jobs:
                # info = job_info(job, verbose=True, textual_color=True)
                await job_list.append(JobListItem(job))

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        """Called when the user moves the selection cursor."""
        if isinstance(event.item, JobListItem):
            job = event.item.job

            # Print to your textual console
            self.log(f"Selected Job id: {job.id}")
