class Event:
    def __init__(self, data = None, redirect = None, action:str = None):
        self.redirect = redirect
        self.action   = action
        self.data     = data

    def __str__(self):
        s = "<Event:"
        if self.redirect: s += f" redirect to {self.redirect.__name__}"
        elif self.action: s += f" action {self.action}"
        elif self.data: s += f" data {str(self.data)}"
        else: s += " EMPTY"
        return s + ">"

EXIT = "exit"