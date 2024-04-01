class Event:
    def __init__(self, data = None, redirect = None, action:str = None):
        self.redirect = redirect
        self.action   = action
        self.data     = data

    def __str__(self): return f"<Event object: redirect {self.redirect}, action {self.action}, data {str(self.data)}"

EXIT = "exit"