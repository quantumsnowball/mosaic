from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Label, ListItem, ListView, Static

from mosaic.jobs.manager import Manager, job_info


# 1. Define the TUI Layout
class Dashboard(App):
    """A simple Textual TUI for managing jobs."""
    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        # header
        yield Header()

        # Create a scrollable list of items
        with Manager() as manager:
            job_infos = [job_info(job) for job in manager.jobs]

        yield ListView(
            *[ListItem(Label(info)) for info in job_infos],
            id="job_list"
        )

        # footer
        yield Footer()
