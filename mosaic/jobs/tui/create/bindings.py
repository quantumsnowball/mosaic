from textual.binding import BindingType

file_tree: list[BindingType] = [
    ("k", "cursor_up", "Up"),
    ("j", "cursor_down", "Down"),
    ("l", "toggle_node", "Toggle node"),
    ("h", "toggle_node", "Toggle node"),
    ("c", "create_lada_job", "Create lada job"),
]

save_as_model_screen = [
    ("escape", "cancel", "Cancel"),
]
