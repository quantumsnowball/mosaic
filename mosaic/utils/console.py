from rich.console import Console

stdout = Console()
stderr = Console(stderr=True)

print = stdout.print
