from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import DirectoryTree


class FileTree(DirectoryTree):
    from .bindings import BINDINGS


class FileList(Vertical):
    def __init__(self) -> None:
        super().__init__(classes='section')
        self.border_title = 'Files'
        self.border_subtitle = 'Files'
        self.directory_tree = FileTree('./')

    def compose(self) -> ComposeResult:
        yield self.directory_tree
