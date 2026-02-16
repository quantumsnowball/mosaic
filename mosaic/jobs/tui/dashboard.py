from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import ContentSwitcher, DirectoryTree, Footer, Header

from mosaic.jobs.tui.delete import JobList


class Dashboard(App):
    """A simple Textual TUI for managing jobs."""

    from .bindings import BINDINGS
    from .styles import CSS

    def __init__(self) -> None:
        super().__init__()
        self._vertical1 = Vertical(classes='section')
        self._vertical2 = Vertical(classes='section')
        self._job_list = JobList(self)
        self._directory_tree = DirectoryTree('./', id='files-view')

    def compose(self) -> ComposeResult:
        # header
        yield Header()

        # job_list ListView
        with self._vertical1:
            yield self._directory_tree
        with self._vertical2:
            yield self._job_list.list_view

        # footer
        yield Footer()

    async def on_mount(self) -> None:
        await self._job_list.list_view.populate()

    def action_delete(self) -> None:
        self._job_list.confirmation.prompt()
