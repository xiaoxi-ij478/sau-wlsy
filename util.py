import contextlib
import dataclasses

class CallbackCaller:
    def __init__(self):
        self.callbacks = []

    def __call__(self, *args, **kwargs):
        for cb in self.callbacks:
            cb(*args, **kwargs)

    def add(self, callback):
        self.callbacks.append(callback)

# a context manager to get rid of busy_hold() / busy_forget() pattern
class HoldWindowContext:
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
    seat_num: int | None
    score: int | None
    report_download_link: str | None

@dataclasses.dataclass
class AvailableClass(ExpClass):
    exp_post_id: int
    is_available: bool = dataclasses.field(default=True, init=False)

# only used for merging results from ExpViewHTMLParser and ExpScoreHTMLParser
def merge_score_only_expclass(score_only, real):
    assert score_only.name == real.name
    assert score_only.teacher == real.teacher

    return ExpClass(
        score_only.name,
        real.time,
        score_only.teacher,
        real.place,
        real.seat_num,
        score_only.score,
        real.report_download_link
    )
