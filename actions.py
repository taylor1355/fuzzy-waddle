class Action():
    def __init__(self, priority, callback):
        self.priority = priority
        self.callback = callback

    def __lt__(self, obj):
        return self.priority < obj.priority

    def execute(self):
        if self.callback:
            self.callback()
