import dataclasses
import html.parser
import io
import itertools
import tkinter
import tkinter.filedialog
import tkinter.messagebox
import tkinter.ttk

from . import about
from . import class_filters
from . import globals as globals_module
from . import util

class TkAvailableClass(util.AvailableClass):
    def __init__(self, name, time, teacher, place, exp_post_id, frame):
        super().__init__(name, time, teacher, place, exp_post_id)
        self.__is_available = True

        self.name_label = tkinter.ttk.Label(frame, text=name)
        self.info_label = tkinter.ttk.Label(
            frame,
            text=
                f"老师：{teacher}\n"
                f"节数：第 {time.week} 周星期 {time.day_of_week} 第 {time.class_time} 节\n"
                f"位置：{place}"
        )
        self.commit_button = tkinter.ttk.Button(
            frame,
            text="选择课程",
            command=self.commit_select
        )

        self.name_label.grid(row=0, column=0, sticky=tkinter.NSEW, padx=10, pady=10)
        self.info_label.grid(row=1, column=0, sticky=tkinter.NSEW, padx=10, pady=10)
        self.commit_button.grid(row=0, column=1, rowspan=2, sticky=tkinter.NSEW, padx=10, pady=10)
        frame.rowconfigure(tkinter.ALL, weight=1)
        frame.columnconfigure(tkinter.ALL, weight=1)

    def commit_select(self):
        if not tkinter.messagebox.askquestion(
            "选课确认",
            f'确认选择 "{self.teacher}" 的 "{self.name}" 课程？'
        ):
            return

        reply = iter(
            globals_module.opener.open(
                "https://wlsy.sau.edu.cn/physlab/stuyy_test2.php",
                urllib.parse.urlencode({
                    "sy_sy": self.exp_post_id,
                    "submit": "添加"
                }).encode()
            )
        )

        # TODO

    @property
    def is_available(self) -> bool:
        return self.__is_available

    @is_available.setter
    def is_available(self, val):
        self.__is_available = val

        try:
            self.name_label
        except AttributeError: # in __init__()
            return

        self.name_label.configure(state=tkinter.NORMAL if val else tkinter.DISABLED)
        self.info_label.configure(state=tkinter.NORMAL if val else tkinter.DISABLED)
        self.commit_button.configure(state=tkinter.NORMAL if val else tkinter.DISABLED)

# fragile HTML parser for experiment class selection page
class ExpSelectPageHTMLParser(html.parser.HTMLParser):
    _NULL_SENTINEL = object()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.parsed_at_least_one_class = False
        self.passed_name_tag = False
        self.parsed_extra_info = False
        self.in_name_tag = False
        self.in_exp_data_tag = False
        self.current_name = ""
        self.current_time = None
        self.current_teacher = ""
        self.current_place = ""
        self.current_exp_post_id = 0
        self.parsed_classes = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        if (
            self.in_exp_data_tag and
            tag == "input" and
            attrs.get("type", self._NULL_SENTINEL) == "radio" and
            attrs.get("name", self._NULL_SENTINEL) == "sy_sy" and
            attrs.get("class", self._NULL_SENTINEL) == "body"
        ):
            if self.passed_name_tag:
                self.parsed_extra_info = False
                self.passed_name_tag = False
                self.parsed_classes.append(
                    util.AvailableClass(
                        self.current_name,
                        self.current_time,
                        self.current_teacher,
                        self.current_place,
                        self.current_exp_post_id
                    )
                )

            self.parsed_at_least_one_class = True
            self.current_exp_post_id = int(attrs["value"])

        if tag == "font" and self.in_exp_data_tag:
            self.in_name_tag = True

        if (
            tag == "form" and
            attrs.get("method", self._NULL_SENTINEL).lower() == "post" and
            attrs.get("action", self._NULL_SENTINEL) == "stuyy_test2.php"
        ):
            self.in_exp_data_tag = True

    def handle_endtag(self, tag):
        if tag == "form" and self.in_exp_data_tag:
            self.in_exp_data_tag = False

            if self.parsed_at_least_one_class:
                self.parsed_classes.append(
                    util.AvailableClass(
                        self.current_name,
                        self.current_time,
                        self.current_teacher,
                        self.current_place,
                        self.current_exp_post_id
                    )
                )

        if tag == "font" and self.in_name_tag:
            self.in_name_tag = False
            self.passed_name_tag = True

    def handle_data(self, data):
        if not self.in_exp_data_tag:
            return

        if self.in_name_tag:
            self.current_name = data

        if self.passed_name_tag and not self.parsed_extra_info:
            self.parsed_extra_info = True

            l = [i.strip() for i in data.split('\xA0') if i.strip()]
            self.current_teacher = l[0].replace("教师：", '')
            self.current_time = util.TimeTuple(*l[1].replace("时间：", '').split(' -'))
            self.current_place = l[2].replace("地点：", '')

def set_all_unavailable():
    for c in available_classes:
        c.is_available = False

def set_all_available():
    for c in available_classes:
        c.is_available = True

# How to write a filter:
# def filter_teacher(aclass):
#     # return True if accept, else return False
#     return aclass.teacher == "blabla"
# add_filter(filter_teacher)

def add_filter(aclass):
    filters.append(aclass)

def exec_filter():
    set_all_available()
    filtered_classes = []

    for f in filters:
        for c in filter(lambda i: not f(i), available_classes):
            if c not in filtered_classes:
                filtered_classes.append(c)

    for c in filtered_classes:
        c.is_available = False

def filter_class_pressed():
    filename = tkinter.filedialog.askopenfilename(
        parent=select_class_toplevel,
        title="选择课程表文件",
        filetypes=[
            ("CSV 文件", "*.csv")
        ]
    )

    if not filename:
        return

    with util.HoldContextManager(select_class_toplevel):
        class_filters.read_class_csv(filename)
        exec_filter()

def filter_teacher_updated(*args):
    with util.HoldContextManager(select_class_toplevel):
        class_filters.allowed_teachers = list(filter(bool, filter_teacher.get().split(',，')))
        exec_filter()

def filter_not_teacher_updated(*args):
    with util.HoldContextManager(select_class_toplevel):
        class_filters.refused_teachers = list(filter(bool, filter_not_teacher.get().split(',，')))
        exec_filter()

def filter_keyword_updated(*args):
    with util.HoldContextManager(select_class_toplevel):
        class_filters.filter_keyword = list(filter(bool, filter_keyword.get().split(',，')))
        exec_filter()

def reload():
    global pages

    with util.HoldContextManager(select_class_toplevel):
        no_class_info_label.grid_remove()

        reply = io.TextIOWrapper(
            globals_module.opener.open(
                "https://wlsy.sau.edu.cn/physlab/stuyy_test2.php"
            )
        )

        parser = ExpSelectPageHTMLParser()
        while buffer := reply.read(1024):
            parser.feed(buffer)

        for f in page_frames:
            f.destroy()

        page_frames.clear()
        available_classes.clear()

        if not parser.parsed_classes:
            no_class_info_label.grid()
            class_list_frame.rowconfigure(tkinter.ALL, weight=1)
            class_list_frame.columnconfigure(tkinter.ALL, weight=1)
            return

        a, b = divmod(len(parser.parsed_classes), ITEMS_PRE_PAGE)
        current_page = 1
        total_pages = a + bool(b)

        for it in itertools.batched(parser.parsed_classes, ITEMS_PRE_PAGE):
            internal_class_frame = tkinter.ttk.Frame(class_list_frame)
            page_frames.append(internal_class_frame)

            for i, c in enumerate(it):
                class_item_frame = tkinter.ttk.Frame(internal_class_frame)
                class_item_frame.grid(row=i, column=0, sticky=tkinter.NSEW, padx=10, pady=10)

                available_classes.append(
                    TkAvailableClass(
                        c.name,
                        c.time,
                        c.teacher,
                        c.place,
                        c.exp_post_id,
                        class_item_frame
                    )
                )

        internal_class_frame.rowconfigure(tkinter.ALL, weight=1)
        internal_class_frame.columnconfigure(tkinter.ALL, weight=1)
        internal_class_frame.grid(row=0, column=0, sticky=tkinter.NSEW)
        class_list_frame.rowconfigure(tkinter.ALL, weight=1)
        class_list_frame.columnconfigure(tkinter.ALL, weight=1)

def activate_self():
    select_class_toplevel.wm_deiconify()
    reload()

ITEMS_PRE_PAGE = 6

current_page = 1
total_pages = 1
filters = []
available_classes: list[TkAvailableClass] = []
page_frames: list[tkinter.ttk.Frame] = []

def next_page():
    if current_page >= total_pages:
        return

    page_frames[current_page - 1].grid_remove()
    page_frames[current_page].grid()
    current_page += 1
    paginator_indicator.set(f"{current_page} / {total_pages} 页")

def prev_page():
    if current_page <= 1:
        return

    page_frames[current_page].grid_remove()
    page_frames[current_page - 1].grid()
    current_page -= 1
    paginator_indicator.set(f"{current_page} / {total_pages} 页")

add_filter(class_filters.filter_refused_times)
add_filter(class_filters.filter_allowed_teacher)
add_filter(class_filters.filter_refused_teacher)
add_filter(class_filters.filter_keyword)

select_class_toplevel = tkinter.Toplevel(globals_module.root)
select_class_toplevel.wm_title("选课 - 物理实验选课系统")
select_class_toplevel.wm_withdraw()
select_class_toplevel.wm_protocol("WM_DELETE_WINDOW", globals_module.exit_func)

select_class_menu = tkinter.Menu(select_class_toplevel, tearoff=False)
select_class_menu.add_command(label="退出", command=globals_module.exit_func)
select_class_menu.add_command(label="关于", command=about.about_toplevel.wm_deiconify)

select_class_toplevel.configure(menu=select_class_menu)

filter_class_label_str = tkinter.StringVar(select_class_toplevel, "选择课程表来过滤课程")
filter_class_label = tkinter.ttk.Label(
    select_class_toplevel,
    textvariable=filter_class_label_str
)
filter_class_button = tkinter.ttk.Button(
    select_class_toplevel,
    text="选择课程表文件...",
    command=filter_class_pressed
)

filter_teacher = tkinter.StringVar(select_class_toplevel)
filter_teacher_label = tkinter.ttk.Label(
    select_class_toplevel,
    text="输入你想要的老师，以逗号分隔"
)
filter_teacher_entry = tkinter.ttk.Entry(
    select_class_toplevel,
    textvariable=filter_teacher
)

filter_not_teacher = tkinter.StringVar(select_class_toplevel)
filter_not_teacher_label = tkinter.ttk.Label(
    select_class_toplevel,
    text="输入你不想要的老师，以逗号分隔\n"
         "（可同时与想要的老师一起使用）"
)
filter_not_teacher_entry = tkinter.ttk.Entry(
    select_class_toplevel,
    textvariable=filter_not_teacher
)

filter_keyword = tkinter.StringVar(select_class_toplevel)
filter_keyword_label = tkinter.ttk.Label(
    select_class_toplevel,
    text="输入你想要的课程，关键词（比如重力加速度）即可，以逗号分隔"
)
filter_keyword_entry = tkinter.ttk.Entry(
    select_class_toplevel,
    textvariable=filter_keyword
)

refresh_button = tkinter.ttk.Button(select_class_toplevel, text="刷新", command=reload)

class_list_frame = tkinter.ttk.Frame(select_class_toplevel)

no_class_info_label = tkinter.ttk.Label(
    class_list_frame,
    text="当前没有课程",
    anchor=tkinter.CENTER
)

paginator_frame = tkinter.ttk.Frame(select_class_toplevel)
paginator_indicator = tkinter.StringVar(paginator_frame, "1 / 1 页")
paginator_left_button = tkinter.ttk.Button(paginator_frame, text="<")
paginator_indicator_label = tkinter.ttk.Label(
    paginator_frame,
    textvariable=paginator_indicator,
    anchor=tkinter.CENTER
)
paginator_right_button = tkinter.ttk.Button(paginator_frame, text=">")

filter_class_label.grid(row=0, column=0, sticky=tkinter.NSEW, padx=10, pady=10)
filter_class_button.grid(row=0, column=1, sticky=tkinter.NSEW, padx=10, pady=10)
filter_teacher_label.grid(row=1, column=0, sticky=tkinter.NSEW, padx=10, pady=10)
filter_teacher_entry.grid(row=1, column=1, sticky=tkinter.NSEW, padx=10, pady=10)
filter_not_teacher_label.grid(row=2, column=0, sticky=tkinter.NSEW, padx=10, pady=10)
filter_not_teacher_entry.grid(row=2, column=1, sticky=tkinter.NSEW, padx=10, pady=10)
filter_keyword_label.grid(row=3, column=0, sticky=tkinter.NSEW, padx=10, pady=10)
filter_keyword_entry.grid(row=3, column=1, sticky=tkinter.NSEW, padx=10, pady=10)
refresh_button.grid(row=4, column=0, columnspan=2, sticky=tkinter.NSEW, padx=10, pady=10)
class_list_frame.grid(row=5, column=0, columnspan=2, sticky=tkinter.NSEW, padx=10, pady=10)
no_class_info_label.grid(row=0, column=0, sticky=tkinter.NSEW)
no_class_info_label.grid_remove()
paginator_left_button.grid(row=0, column=0, sticky=tkinter.NSEW, padx=10, pady=10)
paginator_indicator_label.grid(row=0, column=1, sticky=tkinter.NSEW, padx=10, pady=10)
paginator_right_button.grid(row=0, column=2, sticky=tkinter.NSEW, padx=10, pady=10)
paginator_frame.grid(row=6, column=0, columnspan=2, sticky=tkinter.NSEW, padx=10, pady=10)
paginator_frame.rowconfigure(tkinter.ALL, weight=1)
paginator_frame.columnconfigure(tkinter.ALL, weight=1)
select_class_toplevel.rowconfigure(tkinter.ALL, weight=1)
select_class_toplevel.columnconfigure(tkinter.ALL, weight=1)
select_class_toplevel.rowconfigure(5, minsize=300, weight=3) # let class list frame show larger
for i in range(5):
    select_class_toplevel.rowconfigure(i, uniform="filter")

select_class_toplevel.rowconfigure(6, uniform="filter")
filter_teacher.trace_add("write", filter_teacher_updated)
filter_not_teacher.trace_add("write", filter_not_teacher_updated)
filter_keyword.trace_add("write", filter_keyword_updated)

globals_module.select_class_activate.add(activate_self)
