from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import ContentSwitcher, DirectoryTree, Footer, Header

from mosaic.jobs.tui.create import FileList
from mosaic.jobs.tui.delete import JobList


class Dashboard(App):
    """A simple Textual TUI for managing jobs."""

    TITLE = 'Mosaic TUI'
    from .bindings import BINDINGS
    from .styles import CSS

    def __init__(self) -> None:
        super().__init__()
        self._job_list = JobList(self)
        self._directory_tree = FileList()

    def compose(self) -> ComposeResult:
        # header
        yield Header()

        # container widgets
        yield self._directory_tree
        yield self._job_list

        # footer
        yield Footer()

    async def on_mount(self) -> None:
        await self._job_list.list_view.populate()

    def action_delete(self) -> None:
        self._job_list.confirmation.prompt()
