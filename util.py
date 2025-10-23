class CallbackCaller:
    def __init__(self):
        self.callbacks = []

    def __call__(self, *args, **kwargs):
        for cb in self.callbacks:
            cb(*args, **kwargs)

    def add(self, callback):
        self.callbacks.append(callback)

# a context manager to get rid of busy_hold() / busy_forget() pattern
class HoldContextManager:
    def __init__(self, window):
        self.window = window

    def __enter__(self):
        self.window.busy_hold()
        self.window.update() # so that cursor can be updated

    def __exit__(self, type, value, traceback):
        self.window.busy_forget()
        self.window.update() # ditto
