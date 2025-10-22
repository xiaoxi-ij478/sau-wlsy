import collections
import csv
import itertools
import tkinter
import tkinter.filedialog
import tkinter.messagebox
import tkinter.ttk

import globals as globals_module

# shamelessly use format from Lemon Timetable
# we use only these rows:
# - week
# - class time
# - day of week
# day of week analysis method:
# each field is splited by '、'
# if there is - then set inclusive range
# if there is '单' or '双' at the end then
#    include only odd or even weeks in the range

# time format:
# (week, day of week, class time)
TimeTuple = collections.namedtuple(
    "TimeTuple",
    [
        "week",
        "day_of_week",
        "class_time"
    ]
)
refused_times = []

def read_class_csv(filename):
    refused_times.clear()

    with open(filename, newline='') as fp:
        reader = iter(csv.reader(fp))

        itertools.dropwhile(lambda i: i[0] != "课程名称", reader)
        next(reader)

        for i in reader:
            for j in i[6].split('、'):
                if '-' not in j:
                    refused_times.append(TimeTuple(int(i[1]), int(i[2]), int(i[6])))
                else:
                    if j.count('-') != 1:
                        tkinter.messagebox.showerror(
                            "错误",
                            "课程周数不合法；格式应为 <开始>-<结束>；\n"
                            f"实际为 '{j}'
                        )
                        return

                    begin, end = j.split('-')
                    begin = int(begin)
                    end = int(end) + 1
                    if begin > end:
                        tkinter.messagebox.showerror(
                            "错误",
                            "课程周数不合法；开始应小于等于结束；\n"
                            f"实际为 '{j}'
                        )
                        return

                    step = 1
                    if end[-1] == '单':
                        if not begin % 2: # 6-11 for example
                            begin += 1
                        step = 2
                    elif end[-1] == '双':
                        if begin % 2: # 7-12 for example
                            begin += 1
                        step = 2
                    for week in range(begin, end, step):
                        refused_times.append(TimeTuple(int(i[1]), int(i[2]), week))

    tkinter.messagebox.showinfo("加载完成", "课程表加载完成")
    filter_class_label_str.set("选择课程表过滤课程（已加载）")

AvailableClass = collections.namedtuple(
    "AvailableClass",
    [
        "name",
        "time",
        "teacher",
        "place",
        "is_available"
    ]
)
current_available_classes = []

def filter_teacher():
    pass

def filter_refused_times():
    return any(t == i for i in refused_times)

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

    read_class_csv(filename)

def refresh():
    reply = globals_module.opener.open(
        "https://wlsy.sau.edu.cn/physlab/stuyy_test2.php"
    ).read()

    

select_class_toplevel = tkinter.Toplevel(globals_module.root)

filter_class_label_str = tkinter.StringVar(select_class_toplevel, "选择课程表过滤课程")
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
         "（如果也同时填写了想要的老师，则以想要的老师进行过滤）"
)
filter_not_teacher_entry = tkinter.ttk.Entry(
    select_class_toplevel,
    textvariable=filter_not_teacher
)

filter_class_type = tkinter.StringVar(select_class_toplevel)
filter_class_type_label = tkinter.ttk.Label(
    select_class_toplevel,
    text="输入你想要的课程，关键词（比如重力加速度）即可，以逗号分隔"
)
filter_class_type_entry = tkinter.ttk.Entry(
    select_class_toplevel,
    textvariable=filter_class_type
)

refresh_button = tkinter.ttk.Button(select_class_toplevel, text="刷新", command=refresh)

class_list_frame = tkinter.ttk.Frame(select_class_toplevel)

paginator_indicator = tkinter.StringVar(select_class_toplevel, "0 / 0 页")
paginator_left_button = tkinter.ttk.Button(select_class_toplevel, text="<")
paginator_indicator_label = tkinter.ttk.Label(select_class_toplevel, textvariable=paginator_indicator)
paginator_right_button = tkinter.ttk.Button(select_class_toplevel, text=">")
