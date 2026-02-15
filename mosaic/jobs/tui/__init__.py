from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Label, ListItem, ListView, Static


# 1. Define the TUI Layout
class Dashboard(App):
    """A simple Textual TUI for managing jobs."""
    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        # header
        yield Header()

        # Create a scrollable list of items
        job_names = [f"Job #{i}: Processing data chunk {i*10}..." for i in range(1, 51)]

        yield ListView(
            *[ListItem(Label(name)) for name in job_names],
            id="job_list"
        )

        # footer
        yield Footer()
