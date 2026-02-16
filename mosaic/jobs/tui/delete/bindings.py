from textual.binding import BindingType

confirmatino_model_screen = [
    ("y", "confirm", "Yes, Delete"),
    ("Y", "confirm", "Yes, Delete"),
    ("n", "cancel", "No, Cancel"),
    ("N", "cancel", "No, Cancel"),
    ("escape", "cancel", "Cancel")
]

list_view: list[BindingType] = [
    ("k", "cursor_up", "Up"),
    ("j", "cursor_down", "Down"),
]
