main = """
    .section {
        border: round $primary 30%;     
        border-title-align: center;
        border-subtitle-align: center;
    }
    .section:focus-within {
        border: round $primary;    
    }
    
    /* must put here at the root, otherwise doesn't work, why? */
    JobList JobListView JobListItem.-highlight {
        /* a very faint background */
        background: $accent 25%;
    }
"""
