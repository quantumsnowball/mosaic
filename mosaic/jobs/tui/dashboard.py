import shutil

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Footer, Header, ListView

from mosaic.jobs.manager import Manager
from mosaic.jobs.tui.delete import JobList
from mosaic.jobs.tui.delete.delete import ConfirmDelete
from mosaic.jobs.tui.delete.list import JobListItem


class Dashboard(App):
    """A simple Textual TUI for managing jobs."""

    from .bindings import BINDINGS
    from .style import CSS

    def __init__(self) -> None:
        super().__init__()
        self._job_list = JobList(self)

    def compose(self) -> ComposeResult:
        # header
        yield Header()

        # job_list ListView
        yield self._job_list.list_view

        # footer
        yield Footer()

    async def on_mount(self) -> None:
        # Populate the list after the UI has started
        list_view = self.query_one("#job_list", ListView)
        with Manager() as manager:
            for job in manager.jobs:
                await list_view.append(JobListItem(job))

    def action_delete(self) -> None:
        self._job_list.prompt_for_delete_confirmation()
