from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Vertical

from mosaic.jobs.tui.create.tree import FileTree

if TYPE_CHECKING:
    from mosaic.jobs.tui.dashboard import Dashboard


class FileList(Vertical):
    def __init__(self, dashboard: Dashboard) -> None:
        super().__init__(classes='section')
        self.border_title = 'Files'
        self.border_subtitle = 'Files'
        self.directory_tree = FileTree(dashboard)

    def compose(self) -> ComposeResult:
        yield self.directory_tree
