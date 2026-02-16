import shutil

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Footer, Header, ListView

from mosaic.jobs.manager import Manager
from mosaic.jobs.tui.delete import JobHandler
from mosaic.jobs.tui.delete.delete import ConfirmDelete
from mosaic.jobs.tui.delete.list import JobListItem


class Dashboard(App):
    """A simple Textual TUI for managing jobs."""

    from .bindings import BINDINGS
    from .style import CSS

    def __init__(self) -> None:
        super().__init__()
        self._job_handler = JobHandler(self)

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
                await job_list.append(JobListItem(job))

    def action_delete(self) -> None:
        self._job_handler.prompt_for_delete_confirmation()
