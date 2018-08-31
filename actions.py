class Action():
    def __init__(self, priority, callback):
        self.priority = priority
        self.callback = callback

    def execute(self):
        if self.callback:
            self.callback()
