import shutil
import subprocess
from pathlib import Path
from subprocess import DEVNULL

from textual.widgets import DirectoryTree


class FileTree(DirectoryTree):
    from .bindings import BINDINGS

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        abs_path = event.path
        rel_path = abs_path.relative_to(Path.cwd())
        self.open_in_vlc(rel_path)

    def open_in_vlc(self, target_path: Path) -> None:
        # try Linux VLC first
        if shutil.which("vlc"):
            subprocess.Popen(["vlc", target_path], stdout=DEVNULL, stderr=DEVNULL)
            self.app.notify(f"Opening in Linux VLC: {target_path}")
            return

        # try Windows VLC Fallback
        vlc_win_path = Path("/mnt/c/Program Files/VideoLAN/VLC/vlc.exe")
        if vlc_win_path.exists():
            target_win_path = subprocess.check_output(["wslpath", "-w", str(target_path)], text=True).strip()
            subprocess.Popen([vlc_win_path, target_win_path], stdout=DEVNULL, stderr=DEVNULL)
            self.app.notify(f"Opening in Windows VLC: {target_path}")
            return

        self.app.notify("VLC not found on Linux or Windows path.", severity="error")
