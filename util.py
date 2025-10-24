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

class TimeTuple:
    def __init__(self, week, day_of_week, class_time):
        self.week = week
        self.day_of_week = day_of_week
        self.class_time = class_time

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
                f"{self.week!r}, "
                f"{self.day_of_week!r}, "
                f"{self.class_time!r}"
            f")"
        )

class AvailableClass:
    def __init__(self, name, time, teacher, place, exp_post_id):
        self.name = name
        self.time = time
        self.teacher = teacher
        self.place = place
        self.exp_post_id = exp_post_id
        self.is_available = True

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
                f"{self.name!r}, "
                f"{self.time!r}, "
                f"{self.teacher!r},"
                f"{self.place!r}, "
                f"{self.exp_post_id!r}, "
                f"{self.is_available!r}"
            f")"
        )

class ChosenClass:
    def __init__(self, name, time, teacher, place, seat_num, report_download_link):
        self.name = name
        self.time = time
        self.teacher = teacher
        self.place = place
        self.seat_num = seat_num
        self.report_download_link = report_download_link

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
                f"{self.name!r}, "
                f"{self.time!r}, "
                f"{self.teacher!r}, "
                f"{self.place!r}, "
                f"{self.seat_num!r}, "
                f"{self.report_download_link!r}"
            f")"
        )
