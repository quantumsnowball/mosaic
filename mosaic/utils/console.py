from rich.console import Console


class RichConsole:
    stdout = Console(highlight=False)
    stderr = Console(highlight=False, stderr=True)


stdout = RichConsole.stdout.print
stderr = RichConsole.stderr.print
