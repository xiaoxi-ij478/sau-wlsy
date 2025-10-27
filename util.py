import dataclasses

class CallbackCaller:
    def __init__(self):
        self.callbacks = []

    def __call__(self, *args, **kwargs):
        for cb in self.callbacks:
            cb(*args, **kwargs)

    def add(self, callback):
        self.callbacks.append(callback)

class HoldWindowContext:
    "a context manager to get rid of busy_hold() / busy_forget() pattern"
    def __init__(self, window):
        self.window = window

    def __enter__(self):
        self.window.busy_hold()
        self.window.update() # so that cursor can be updated

    def __exit__(self, *args):
        self.window.busy_forget()
        self.window.update() # ditto

@dataclasses.dataclass
class TimeTuple:
    week: int
    day_of_week: int
    class_time: int

@dataclasses.dataclass
class ExpClass:
    name: str
    time: TimeTuple
    teacher: str
    place: str | None

@dataclasses.dataclass
class AvailableClass(ExpClass):
    post_id: int
    is_available: bool = dataclasses.field(default=True, init=False)

@dataclasses.dataclass
class ChosenClass(ExpClass):
    seat_num: int | None
    score: int | None
    report_download_link: str | None
    can_cancel: bool
    post_id: int | None
