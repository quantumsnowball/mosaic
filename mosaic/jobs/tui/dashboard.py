import shutil

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Footer, Header, ListView

from mosaic.jobs.manager import Manager
from mosaic.jobs.tui.delete.delete import ConfirmDelete
from mosaic.jobs.tui.delete.list import JobListItem


class Dashboard(App):
    """A simple Textual TUI for managing jobs."""

    from .bindings import BINDINGS
    from .style import CSS

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
        item = self.query_one("#job_list", ListView).highlighted_child
        if isinstance(item, JobListItem):
            self.push_screen(ConfirmDelete(), self.handle_delete_result)

    def handle_delete_result(self, confirmed: bool | None) -> None:
        if not confirmed:
            return

        item = self.query_one("#job_list", ListView).highlighted_child

        if not isinstance(item, JobListItem):
            self.notify(f'Failed to get job info', severity='error')
            return

        job = item.job

        try:
            if job.job_dirpath.exists():
                shutil.rmtree(job.job_dirpath)
            item.remove()
            self.notify(f"Job {job.id} deleted.")
        except Exception as e:
            self.notify(f"Failed to delete: {e}", severity="error")
