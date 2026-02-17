from pathlib import Path

from textual.widgets import DirectoryTree


class FileTree(DirectoryTree):
    from .bindings import BINDINGS

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        abs_path = event.path
        rel_path = abs_path.relative_to(Path.cwd())
        self.log(f"FILE SELECTED: {rel_path}")
        self.app.notify(f"Selected: [bold cyan]{rel_path}[/]", title="File Browser")
