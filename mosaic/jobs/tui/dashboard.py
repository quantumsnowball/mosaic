from textual.app import App, ComposeResult
from textual.widgets import Footer, Header

from mosaic.jobs.tui.create import FileList
from mosaic.jobs.tui.delete import JobList


class Dashboard(App):
    """A simple Textual TUI for managing jobs."""

    TITLE = 'Mosaic TUI'
    from .bindings import dashboard as BINDINGS
    from .styles import dashboard as CSS

    def __init__(self) -> None:
        super().__init__()
        self.job_list = JobList(self)
        self.directory_tree = FileList(self)

    def compose(self) -> ComposeResult:
        # header
        yield Header()

        # container widgets
        yield self.directory_tree
        yield self.job_list

        # footer
        yield Footer()

    async def on_mount(self) -> None:
        await self.job_list.list_view.populate()

    def action_delete(self) -> None:
        self.job_list.confirmation.prompt()
