from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Footer, Header, Label, ListItem, ListView

from mosaic.jobs.manager import Manager
from mosaic.jobs.text import job_info


# 1. Define the TUI Layout
class Dashboard(App):
    """A simple Textual TUI for managing jobs."""
    CSS = """
    #main-window {
        border: round $primary;      /* The window frame */
        border-title-align: center;  /* Center the title */
        margin: 1 2;                 /* Breathing room from screen edges */
        background: $surface;
    }
    
    #job_list {
        background: transparent;
    }
    """

    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        # header
        yield Header()

        # Create a Vertical container to be the main window frame
        with Vertical(id='main-window') as v:
            v.border_title = 'JOBS'
            yield ListView(id='job_list')

        # footer
        yield Footer()

    async def on_mount(self) -> None:
        # Populate the list after the UI has started
        job_list = self.query_one("#job_list", ListView)
        with Manager() as manager:
            for job in manager.jobs:
                info = job_info(job)
                await job_list.append(ListItem(Label(info)))
