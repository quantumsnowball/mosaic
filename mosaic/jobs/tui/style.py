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

    #job_list > ListItem.-highlight {
        /* a very faint background */
        background: $accent 25%;
    }
"""
