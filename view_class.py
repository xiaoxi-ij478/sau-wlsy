import dataclasses
import email.headerregistry
import io
import itertools
import textwrap
import tkinter
import tkinter.filedialog
import tkinter.messagebox
import tkinter.ttk
import urllib.parse

from . import about
from . import globals as globals_module
from . import html_parsers
from . import util

def merge_score_only_expclass(score_only, real):
    "only used for merging results from ExpViewHTMLParser and ExpScoreHTMLParser"
    assert score_only.name == real.name
    assert score_only.teacher == real.teacher

    return util.ChosenClass(
        score_only.name,
        real.time,
        score_only.teacher,
        real.place,
        real.seat_num,
        score_only.score,
        real.report_download_link,
        real.can_cancel,
        real.post_id
    )

def merge_cancel_expclass(cancel, real):
    "only used for merging results from ExpViewHTMLParser and ExpCancelHTMLParser"
    assert cancel.name == real.name
    assert cancel.time == real.time

    return util.ChosenClass(
        cancel.name,
        cancel.time,
        real.teacher,
        real.place,
        real.seat_num,
        real.score,
        real.report_download_link,
        cancel.can_cancel,
        cancel.post_id
    )

@dataclasses.dataclass
class TkChosenClass(util.ChosenClass):
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
    download_report_button: tkinter.ttk.Button = dataclasses.field(
        init=False,
        repr=False,
        compare=False
    )
    remove_class_button: tkinter.ttk.Button = dataclasses.field(
        init=False,
        repr=False,
        compare=False
    )

    def __post_init__(self, frame):
        self.name_label = tkinter.ttk.Label(frame, text=self.name)
        self.info_label = tkinter.ttk.Label(
            frame,
            text=textwrap.dedent(f"""\
            老师：{self.teacher}
            节数：第 {self.time.week} 周星期 {self.time.day_of_week} 第 {self.time.class_time} 节
            位置：{self.place}

            座位号：{"还没有分配座位" if self.seat_num is None else self.seat_num}
            分数：{"还没有打分" if self.score is None else self.score}\
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
            command=self.remove_class,
            state=tkinter.NORMAL if self.can_cancel else tkinter.DISABLED
        )

        self.name_label.grid(row=0, column=0, sticky=tkinter.NSEW, padx=10, pady=10)
        self.info_label.grid(row=1, column=0, sticky=tkinter.NSEW, padx=10, pady=10)
        self.download_report_button.grid(row=0, column=1, sticky=tkinter.EW, padx=10, pady=10)
        self.remove_class_button.grid(row=1, column=1, sticky=tkinter.EW, padx=10, pady=10)
        frame.rowconfigure(tkinter.ALL, weight=1)
        frame.columnconfigure(tkinter.ALL, weight=1)

    def download_report(self):
        with util.HoldWindowContext(view_class_toplevel):
            reply = globals_module.opener.open(self.report_download_link)
            # very awkward usage, but very effective
            default_filename = urllib.parse.unquote(
                email.headerregistry.HeaderRegistry()(
                    "Content-Disposition",
                    reply.headers["Content-Disposition"]
                ).params["filename"]
            )

            fp = tkinter.filedialog.asksaveasfile(
                master=view_class_toplevel,
                mode="wb",
                title="选择报告保存位置",
                initialfile=default_filename,
                filetypes=[
                    ("PDF 文件", "*.pdf")
                ]
            )
            if fp is None:
                return

            def _internal_download_func():
                if buffer := reply.read(32768):
                    fp.write(buffer)
                    globals_module.root.after(0, _internal_download_func)

                else:
                    fp.close()
                    tkinter.messagebox.showinfo(
                        "报告下载完成",
                        f'报告已下载到 "{fp.name}"。',
                        master=view_class_toplevel
                    )

            _internal_download_func()

    def remove_class(self):
        if tkinter.messagebox.askquestion(
            "选课确认",
            f'确认选择 "{self.teacher}" 的 "{self.name}" 课程？',
            master=view_class_toplevel
        ) != tkinter.YES:
            return

        reply = io.TextIOWrapper(
            globals_module.opener.open(
                "https://wlsy.sau.edu.cn/physlab/stuqxyy.php",
                urllib.parse.urlencode({"sy_qx": self.post_id}).encode()
            )
        )

        # TODO

def reload():
    with util.HoldWindowContext(view_class_toplevel):
        global current_page
        global total_pages

        no_class_info_label.grid_remove()

        reply1 = io.TextIOWrapper(
            globals_module.opener.open(
                "https://wlsy.sau.edu.cn/physlab/stuyycx.php"
            )
        )
        reply2 = io.TextIOWrapper(
            globals_module.opener.open(
                "https://wlsy.sau.edu.cn/physlab/stuqxyy.php"
            )
        )
        reply3 = io.TextIOWrapper(
            globals_module.opener.open(
                "https://wlsy.sau.edu.cn/physlab/scjcx.php"
            )
        )
        parser1 = html_parsers.ExpViewHTMLParser()
        parser2 = html_parsers.ExpCancelHTMLParser()
        parser3 = html_parsers.ExpScoreHTMLParser()

        for line in reply1:
            parser1.feed(line)

        for line in reply2:
            parser2.feed(line)

        for line in reply3:
            parser3.feed(line)

        page_frames.clear()
        all_classes.clear()
        for f in page_frames:
            f.destroy()

        tmp_all_classes = []

        for real in parser1.parsed_classes:
            for cancel in parser2.parsed_classes:
                if real.name == cancel.name:
                    real = merge_cancel_expclass(cancel, real)
                    break

            for score_only in parser3.parsed_classes:
                if real.name == score_only.name:
                    real = merge_score_only_expclass(score_only, real)
                    break

            tmp_all_classes.append(real)

        if not tmp_all_classes:
            no_class_info_label.grid()
            class_list_frame.rowconfigure(tkinter.ALL, weight=1)
            class_list_frame.columnconfigure(tkinter.ALL, weight=1)
            return

        a, b = divmod(len(tmp_all_classes), globals_module.items_pre_page)
        current_page = 1
        total_pages = a + bool(b)

        for it in itertools.batched(
            tmp_all_classes,
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

                all_classes.append(
                    TkChosenClass(
                        c.name,
                        c.time,
                        c.teacher,
                        c.place,
                        c.seat_num,
                        c.score,
                        c.report_download_link,
                        c.can_cancel,
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
    view_class_toplevel.wm_deiconify()
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

def back():
    view_class_toplevel.wm_withdraw()
    globals_module.nav_activate()

current_page = 1
total_pages = 1
all_classes = []
page_frames = []

view_class_toplevel = tkinter.Toplevel(globals_module.root)
view_class_toplevel.wm_title("查看课程 - 物理实验选课系统")
view_class_toplevel.wm_withdraw()
view_class_toplevel.wm_protocol("WM_DELETE_WINDOW", globals_module.exit_func)

view_class_menu = tkinter.Menu(view_class_toplevel, tearoff=False)
view_class_menu.add_command(label="退出", command=globals_module.exit_func)
view_class_menu.add_command(
    label="关于",
    command=lambda: globals_module.about_activate(view_class_toplevel)
)
view_class_toplevel.configure(menu=view_class_menu)

title_label = tkinter.ttk.Label(
    view_class_toplevel,
    text="查看课程",
    anchor=tkinter.CENTER,
    font=tkinter.font.Font(view_class_toplevel, size=16)
)

refresh_button = tkinter.ttk.Button(
    view_class_toplevel,
    text="刷新",
    command=reload
)

class_list_frame = tkinter.ttk.Frame(view_class_toplevel)

no_class_info_label = tkinter.ttk.Label(
    class_list_frame,
    text="当前没有课程",
    anchor=tkinter.CENTER
)

paginator_indicator = tkinter.StringVar(view_class_toplevel, "1 / 1 页")
paginator_left_button = tkinter.ttk.Button(
    view_class_toplevel,
    text="<",
    command=prev_page
)
paginator_indicator_label = tkinter.ttk.Label(
    view_class_toplevel,
    textvariable=paginator_indicator,
    anchor=tkinter.CENTER
)
paginator_right_button = tkinter.ttk.Button(
    view_class_toplevel,
    text=">",
    command=next_page
)

back_button = tkinter.ttk.Button(
    view_class_toplevel,
    text="返回",
    command=back
)

title_label.grid(row=0, column=0, columnspan=3, sticky=tkinter.NSEW, padx=10, pady=10)
refresh_button.grid(row=1, column=0, columnspan=3, sticky=tkinter.NSEW, padx=10, pady=10)
class_list_frame.grid(row=2, column=0, columnspan=3, sticky=tkinter.NSEW, padx=10, pady=10)
no_class_info_label.grid(row=0, column=0, sticky=tkinter.NSEW)
no_class_info_label.grid_remove()
paginator_left_button.grid(row=3, column=0, sticky=tkinter.NSEW, padx=10, pady=10)
paginator_indicator_label.grid(row=3, column=1, sticky=tkinter.NSEW, padx=10, pady=10)
paginator_right_button.grid(row=3, column=2, sticky=tkinter.NSEW, padx=10, pady=10)
back_button.grid(row=4, column=0, columnspan=3, sticky=tkinter.NSEW, padx=10, pady=10)
view_class_toplevel.rowconfigure(tkinter.ALL, weight=1)
view_class_toplevel.columnconfigure(tkinter.ALL, weight=1)
view_class_toplevel.rowconfigure(2, minsize=300, weight=3) # let class list frame show larger

globals_module.view_class_activate.add(activate_self)
