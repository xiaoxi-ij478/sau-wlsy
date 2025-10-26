import dataclasses
import textwrap
import tkinter
import tkinter.ttk

from . import globals as globals_module
from . import html_parsers
from . import util

@dataclasses.dataclass
class TkExpClass(util.ExpClass):
    frame: dataclasses.InitVar[tkinter.ttk.Frame]
    name_label: tkinter.ttk.Label
    info_label: tkinter.ttk.Label
    commit_button: tkinter.ttk.Button

    def __post_init__(self):
        self.name_label = tkinter.ttk.Label(frame, text=name)
        self.info_label = tkinter.ttk.Label(
            frame,
            text=textwrap.dedent(
            f"""\
    老师：{self.teacher}
    节数：第 {self.time.week} 周星期 {self.time.day_of_week} 第 {self.time.class_time} 节
    位置：{self.place}\
"""
            )
        )
        self.download_report_button = tkinter.ttk.Button(
            frame,
            text="下载报告",
            command=self.download_report
        )
        self.remove_class_button = tkinter.ttk.Button(
            frame,
            text="退课",
            command=self.remove_class
        )

        self.name_label.grid(row=0, column=0, sticky=tkinter.NSEW, padx=10, pady=10)
        self.info_label.grid(row=1, column=0, sticky=tkinter.NSEW, padx=10, pady=10)
        self.download_report_button.grid(
            row=0,
            column=1,
            sticky=tkinter.EW,
            padx=10,
            pady=10
        )
        self.remove_class_button.grid(
            row=1,
            column=1,
            sticky=tkinter.EW,
            padx=10,
            pady=10
        )
        frame.rowconfigure(tkinter.ALL, weight=1)
        frame.columnconfigure(tkinter.ALL, weight=1)

def reload():
    with util.HoldWindowContext(view_class_toplevel):
        pass

view_class_toplevel = tkinter.Toplevel(globals_module.root)
view_class_toplevel.wm_title("查看课程 - 物理实验选课系统")
view_class_toplevel.wm_withdraw()
view_class_toplevel.wm_protocol("WM_DELETE_WINDOW", globals_module.exit_func)

refresh_button = tkinter.ttk.Button(
    view_class_toplevel,
    text="刷新",
    command=reload
)

class_list_frame = tkinter.ttk.Frame(view_class_toplevel)

