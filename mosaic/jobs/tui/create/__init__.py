from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import DirectoryTree


class FileTree(DirectoryTree):
    from .bindings import BINDINGS

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        abs_path = event.path
        rel_path = abs_path.relative_to(Path.cwd())
        self.log(f"FILE SELECTED: {rel_path}")
        self.app.notify(f"Selected: [bold cyan]{rel_path}[/]", title="File Browser")


class FileList(Vertical):
    def __init__(self) -> None:
        super().__init__(classes='section')
        self.border_title = 'Files'
        self.border_subtitle = 'Files'
        self.directory_tree = FileTree('./')

    def compose(self) -> ComposeResult:
        yield self.directory_tree
