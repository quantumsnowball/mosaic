import shutil
import subprocess
from pathlib import Path
from subprocess import DEVNULL
from typing import TYPE_CHECKING

from textual.widgets import DirectoryTree

from mosaic.jobs.job.lada import LadaJob
from mosaic.jobs.tui.create.save import SaveAsModalScreen
from mosaic.utils.time import HMS

if TYPE_CHECKING:
    from mosaic.jobs.tui import Main


class FileTree(DirectoryTree):
    from .bindings import file_tree as BINDINGS

    def __init__(self, main: Main, *, path: str | Path = './') -> None:
        super().__init__(path)
        self.main = main

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        abs_path = event.path
        rel_path = abs_path.relative_to(Path.cwd())
        self.open_in_vlc(rel_path)

    def open_in_vlc(self, target_path: Path) -> None:
        # try Linux VLC first
        if shutil.which("vlc"):
            subprocess.Popen(["vlc", target_path], stdout=DEVNULL, stderr=DEVNULL)
            self.main.notify(f"Opening in Linux VLC: {target_path}")
            return

        # try Windows VLC Fallback
        vlc_win_path = Path("/mnt/c/Program Files/VideoLAN/VLC/vlc.exe")
        if vlc_win_path.exists():
            target_win_path = subprocess.check_output(["wslpath", "-w", str(target_path)], text=True).strip()
            subprocess.Popen([vlc_win_path, target_win_path], stdout=DEVNULL, stderr=DEVNULL)
            self.main.notify(f"Opening in Windows VLC: {target_path}")
            return

        self.main.notify("VLC not found on Linux or Windows path.", severity="error")

    def action_create_lada_job(self) -> None:
        if not self.cursor_node or not self.cursor_node.data:
            self.notify('Error when retrieving file node data')
            return

        input_abs_path = self.cursor_node.data.path
        input_rel_path = input_abs_path.relative_to(Path.cwd())

        if not input_rel_path.is_file():
            self.notify('Select a valid file to create lada job')
            return

        async def handle_submit(user_input: str | None) -> None:
            if user_input:
                output_rel_path = Path(user_input)
                self.main.notify(f"Creating job: {input_rel_path} -> {output_rel_path}")
                with LadaJob.create(
                    segment_time=HMS(0, 5, 0),
                    input_file=input_rel_path,
                    output_file=output_rel_path,
                ) as job:
                    # save
                    job.save()
                    # initialize
                    job.initialize()
                await self.main.job_list.list_view.populate()
            else:
                self.notify("Job creation cancelled")

        self.main.push_screen(SaveAsModalScreen(input_rel_path), handle_submit)
