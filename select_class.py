import dataclasses
import io
import itertools
import re
import textwrap
import tkinter
import tkinter.filedialog
import tkinter.font
import tkinter.messagebox
import tkinter.ttk
import urllib.parse

from . import about
from . import class_filters
from . import globals as globals_module
from . import html_parsers
from . import util

@dataclasses.dataclass
class TkAvailableClass(util.AvailableClass):
    frame: dataclasses.InitVar[tkinter.ttk.Frame]
    name_label: tkinter.ttk.Label = dataclasses.field(
        init=False,
        repr=False,
        compare=False
    )
    info_label: tkinter.ttk.Label = dataclasses.field(
        init=False,
        repr=False,
        compare=False
    )
    commit_button: tkinter.ttk.Button = dataclasses.field(
        init=False,
        repr=False,
        compare=False
    )

    # __is_available is just a internal variable storing real "is_available" value
    # so do not declare it in the class body

    @property
    def is_available(self):
        return self.__is_available

    @is_available.setter
    def is_available(self, val):
        self.__is_available = val

        try:
            self.name_label
        except AttributeError: # still in __init__()
            return

        self.name_label.configure(
            state=tkinter.NORMAL if val else tkinter.DISABLED
        )
        self.info_label.configure(
            state=tkinter.NORMAL if val else tkinter.DISABLED
        )
        self.commit_button.configure(
            state=tkinter.NORMAL if val else tkinter.DISABLED
        )

    def __post_init__(self, frame):
        self.name_label = tkinter.ttk.Label(frame, text=self.name)
        self.info_label = tkinter.ttk.Label(
            frame,
            text=textwrap.dedent(f"""\
            老师：{self.teacher}
            节数：第 {self.time.week} 周星期 {self.time.day_of_week} 第 {self.time.class_time} 节
            位置：{self.place}\
"""
            )
        )
        self.commit_button = tkinter.ttk.Button(
            frame,
            text="选择课程",
            command=self.commit_select
        )

        self.name_label.grid(row=0, column=0, sticky=tkinter.NSEW, padx=10, pady=10)
        self.info_label.grid(row=1, column=0, sticky=tkinter.NSEW, padx=10, pady=10)
        self.commit_button.grid(row=0, column=1, rowspan=2, sticky=tkinter.EW, padx=10, pady=10)
        frame.rowconfigure(tkinter.ALL, weight=1)
        frame.columnconfigure(tkinter.ALL, weight=1)

    def commit_select(self):
        if tkinter.messagebox.askquestion(
            None,
            f'确认选择 "{self.teacher}" 的 "{self.name}" 课程？',
            master=select_class_toplevel
        ) != tkinter.YES:
            return

        reply = io.TextIOWrapper(
            globals_module.opener.open(
                "https://wlsy.sau.edu.cn/physlab/stuyy_test2.php",
                urllib.parse.urlencode({
                    "sy_sy": self.post_id,
                    "submit": "添加"
                }).encode()
            )
        )

        parser = html_parsers.ExpSelectResultHTMLParser()
        while buffer := reply.read(1024):
            parser.feed(buffer)

        if parser.success:
            tkinter.messagebox.showinfo(
                None,
                f'课程 "{self.name}" 已成功选择。',
                master=select_class_toplevel
            )
        else:
            tkinter.messagebox.showerror(
                None,
                f'课程 "{self.name}" 选择失败。\n'
                f"（服务端提示：{parser.notif_data}）",
                master=select_class_toplevel
            )


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
        for c in itertools.filterfalse(f, available_classes):
            if c not in filtered_classes:
                filtered_classes.append(c)

    for c in filtered_classes:
        c.is_available = False

def filter_class_pressed():
    with util.HoldWindowContext(select_class_toplevel):
        filename = tkinter.filedialog.askopenfilename(
            parent=select_class_toplevel,
            title="选择课程表文件",
            filetypes=[
                ("CSV 文件", "*.csv")
            ]
        )

        if not filename:
            return

        class_filters.read_class_csv(filename)
        exec_filter()

comma_spliter = re.compile("[,，]")

def filter_teacher_updated(*args):
    with util.HoldWindowContext(select_class_toplevel):
        class_filters.allowed_teachers = list(
            filter(
                None,
                comma_spliter.split(filter_teacher.get())
            )
        )
        exec_filter()

def filter_not_teacher_updated(*args):
    with util.HoldWindowContext(select_class_toplevel):
        class_filters.refused_teachers = list(
            filter(
                None,
                comma_spliter.split(filter_not_teacher.get())
            )
        )
        exec_filter()

def filter_keyword_updated(*args):
    with util.HoldWindowContext(select_class_toplevel):
        class_filters.filter_keyword = list(
            filter(
                None,
                comma_spliter.split(filter_keyword.get())
            )
        )
        exec_filter()

def reload():
    with util.HoldWindowContext(select_class_toplevel):
        global current_page
        global total_pages

        no_class_info_label.grid_remove()

        reply = io.TextIOWrapper(
            globals_module.opener.open(
                "https://wlsy.sau.edu.cn/physlab/stuyy_test2.php"
            )
        )
        parser = html_parsers.ExpSelectPageHTMLParser()
        while buffer := reply.read(1024):
            parser.feed(buffer)

        page_frames.clear()
        available_classes.clear()
        for f in page_frames:
            f.destroy()

        if not parser.parsed_classes:
            no_class_info_label.grid()
            class_list_frame.rowconfigure(tkinter.ALL, weight=1)
            class_list_frame.columnconfigure(tkinter.ALL, weight=1)
            return

        a, b = divmod(len(parser.parsed_classes), globals_module.items_pre_page)
        current_page = 1
        total_pages = a + bool(b)

        for it in itertools.batched(
            parser.parsed_classes,
            globals_module.items_pre_page
        ):
            internal_class_frame = tkinter.ttk.Frame(class_list_frame)
            page_frames.append(internal_class_frame)

            for i, c in enumerate(it):
                class_item_frame = tkinter.ttk.Frame(internal_class_frame)
                class_item_frame.grid(
                    row=i,
                    column=0,
                    sticky=tkinter.NSEW,
                    padx=10,
                    pady=10
                )

                available_classes.append(
                    TkAvailableClass(
                        c.name,
                        c.time,
                        c.teacher,
                        c.place,
                        c.post_id,
                        class_item_frame
                    )
                )

            internal_class_frame.rowconfigure(tkinter.ALL, weight=1)
            internal_class_frame.columnconfigure(tkinter.ALL, weight=1)
            internal_class_frame.grid(row=0, column=0, sticky=tkinter.NSEW)
            internal_class_frame.grid_remove()

        page_frames[0].grid()
        class_list_frame.rowconfigure(tkinter.ALL, weight=1)
        class_list_frame.columnconfigure(tkinter.ALL, weight=1)
        paginator_indicator.set(f"{current_page} / {total_pages} 页")

def activate_self():
    select_class_toplevel.wm_deiconify()
    reload()

def next_page():
    global current_page
    global total_pages

    if current_page >= total_pages:
        return

    page_frames[current_page - 1].grid_remove()
    page_frames[current_page].grid()
    current_page += 1
    paginator_indicator.set(f"{current_page} / {total_pages} 页")

def prev_page():
    global current_page
    global total_pages

    if current_page <= 1:
        return

    current_page -= 1
    page_frames[current_page].grid_remove()
    page_frames[current_page - 1].grid()
    paginator_indicator.set(f"{current_page} / {total_pages} 页")

def toggle_filters():
    global filters_collapsed

    if filters_collapsed:
        filter_frame.grid()
        title_label.grid(columnspan=1)
        toggle_filter_button_str.set("收起过滤器")
    else:
        filter_frame.grid_remove()
        title_label.grid(columnspan=2)
        toggle_filter_button_str.set("展开过滤器")

    filters_collapsed = not filters_collapsed

def back():
    select_class_toplevel.wm_withdraw()
    globals_module.nav_activate()

def timetable_loaded():
    filter_class_label_str.set("选择课程表来过滤课程（已加载）")

filters_collapsed = False
current_page = 1
total_pages = 1
filters = []
available_classes = []
page_frames = []

select_class_toplevel = tkinter.Toplevel(globals_module.root)
select_class_toplevel.wm_title("选课 - 物理实验选课系统")
select_class_toplevel.wm_withdraw()
select_class_toplevel.wm_protocol("WM_DELETE_WINDOW", globals_module.exit_func)

select_class_menu = tkinter.Menu(select_class_toplevel, tearoff=False)
select_class_menu.add_command(label="退出", command=globals_module.exit_func)
select_class_menu.add_command(
    label="关于",
    command=lambda: globals_module.about_activate(select_class_toplevel)
)
select_class_toplevel.configure(menu=select_class_menu)

title_label = tkinter.ttk.Label(
    select_class_toplevel,
    text="选课",
    anchor=tkinter.CENTER,
    font=tkinter.font.Font(select_class_toplevel, size=16)
)

filter_frame = tkinter.ttk.Frame(select_class_toplevel)

filter_class_label_str = tkinter.StringVar(filter_frame, "选择课程表来过滤课程")
filter_class_label = tkinter.ttk.Label(
    filter_frame,
    textvariable=filter_class_label_str
)
filter_class_button = tkinter.ttk.Button(
    filter_frame,
    text="选择课程表文件...",
    command=filter_class_pressed
)

filter_teacher = tkinter.StringVar(filter_frame)
filter_teacher_label = tkinter.ttk.Label(
    filter_frame,
    text="输入你想要的老师，以逗号分隔"
)
filter_teacher_entry = tkinter.ttk.Entry(filter_frame, textvariable=filter_teacher)

filter_not_teacher = tkinter.StringVar(filter_frame)
filter_not_teacher_label = tkinter.ttk.Label(
    filter_frame,
    text="输入你不想要的老师，以逗号分隔\n"
         "（可同时与想要的老师一起使用）"
)
filter_not_teacher_entry = tkinter.ttk.Entry(
    filter_frame,
    textvariable=filter_not_teacher
)

filter_keyword = tkinter.StringVar(filter_frame)
filter_keyword_label = tkinter.ttk.Label(
    filter_frame,
    text="输入你想要的课程，关键词（比如重力加速度）即可，以逗号分隔"
)
filter_keyword_entry = tkinter.ttk.Entry(filter_frame, textvariable=filter_keyword)

toggle_filter_button_str = tkinter.StringVar(select_class_toplevel, "收起过滤器")
toggle_filter_button = tkinter.ttk.Button(
    select_class_toplevel,
    textvariable=toggle_filter_button_str,
    command=toggle_filters
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
paginator_left_button = tkinter.ttk.Button(
    paginator_frame,
    text="<",
    command=prev_page
)
paginator_indicator_label = tkinter.ttk.Label(
    paginator_frame,
    textvariable=paginator_indicator,
    anchor=tkinter.CENTER
)
paginator_right_button = tkinter.ttk.Button(
    paginator_frame,
    text=">",
    command=next_page
)

back_button = tkinter.ttk.Button(
    select_class_toplevel,
    text="返回",
    command=back
)

title_label.grid(row=0, column=0, sticky=tkinter.NSEW, padx=10, pady=10)
filter_class_label.grid(row=0, column=0, sticky=tkinter.NSEW, padx=10, pady=10)
filter_class_button.grid(row=0, column=1, sticky=tkinter.NSEW, padx=10, pady=10)
filter_teacher_label.grid(row=1, column=0, sticky=tkinter.NSEW, padx=10, pady=10)
filter_teacher_entry.grid(row=1, column=1, sticky=tkinter.NSEW, padx=10, pady=10)
filter_not_teacher_label.grid(row=2, column=0, sticky=tkinter.NSEW, padx=10, pady=10)
filter_not_teacher_entry.grid(row=2, column=1, sticky=tkinter.NSEW, padx=10, pady=10)
filter_keyword_label.grid(row=3, column=0, sticky=tkinter.NSEW, padx=10, pady=10)
filter_keyword_entry.grid(row=3, column=1, sticky=tkinter.NSEW, padx=10, pady=10)
filter_frame.grid(row=2, column=0, sticky=tkinter.NSEW, padx=10, pady=10)
filter_frame.rowconfigure(tkinter.ALL, weight=1, uniform="filter")
filter_frame.columnconfigure(tkinter.ALL, weight=1)
toggle_filter_button.grid(row=3, column=0, sticky=tkinter.NSEW, padx=10, pady=10)
refresh_button.grid(row=4, column=0, sticky=tkinter.NSEW, padx=10, pady=10)
class_list_frame.grid(row=5, column=0, sticky=tkinter.NSEW, padx=10, pady=10)
no_class_info_label.grid(row=0, column=0, sticky=tkinter.NSEW)
no_class_info_label.grid_remove()
paginator_left_button.grid(row=0, column=0, sticky=tkinter.NSEW, padx=10, pady=10)
paginator_indicator_label.grid(row=0, column=1, sticky=tkinter.NSEW, padx=10, pady=10)
paginator_right_button.grid(row=0, column=2, sticky=tkinter.NSEW, padx=10, pady=10)
paginator_frame.grid(row=6, column=0, sticky=tkinter.NSEW, padx=10, pady=10)
back_button.grid(row=7, column=0, sticky=tkinter.NSEW, padx=10, pady=10)
paginator_frame.rowconfigure(tkinter.ALL, weight=1)
paginator_frame.columnconfigure(tkinter.ALL, weight=1)
select_class_toplevel.rowconfigure(tkinter.ALL, weight=1)
select_class_toplevel.columnconfigure(tkinter.ALL, weight=1)
select_class_toplevel.rowconfigure(5, minsize=300, weight=3) # let class list frame show larger
filter_teacher.trace_add("write", filter_teacher_updated)
filter_not_teacher.trace_add("write", filter_not_teacher_updated)
filter_keyword.trace_add("write", filter_keyword_updated)

add_filter(class_filters.filter_refused_times)
add_filter(class_filters.filter_allowed_teacher)
add_filter(class_filters.filter_refused_teacher)
add_filter(class_filters.filter_keyword)

globals_module.select_class_activate.add(activate_self)
