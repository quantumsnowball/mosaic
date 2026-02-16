from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import DirectoryTree


class FileList(Vertical):
    def __init__(self) -> None:
        super().__init__(classes='section')
        self.directory_tree = DirectoryTree('./', id='directory-tree')

    def compose(self) -> ComposeResult:
        yield self.directory_tree
