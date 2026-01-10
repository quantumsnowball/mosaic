from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Static


# 1. Define the TUI Layout
class Dashboard(App):
    """A simple Textual TUI for managing jobs."""
    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Welcome to the Jobs TUI! Press 'q' to exit.")
        yield Footer()
