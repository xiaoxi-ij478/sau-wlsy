import enum
import html.parser
import tkinter
import tkinter.ttk

from . import globals as globals_module
from . import util

class ExpViewHTMLParseStage(enum.IntEnum):
    NONE = enum.auto()
    STU_ID = enum.auto()
    NAME = enum.auto()
    TEACHER = enum.auto()
    TIME = enum.auto()
    PLACE = enum.auto()
    SEAT = enum.auto()
    REPORT_DOWNLOAD_LINK = enum.auto()

    def next_stage(self):
        return type(self)(self + 1)

class ExpViewHTMLParser(html.parser.HTMLParser):
    _NULL_SENTINEL = object()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.current_name = ""
        self.current_teacher = ""
        self.current_time = ""
        self.current_place = ""
        self.current_seat = ""
        self.current_report_download_link = ""
        self.in_exp_table = False
        self.in_exp_line = False
        self.in_download = False
        self.parse_stage = ExpViewHTMLParseStage.NONE
        self.parsed_classes = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        if tag == "a" and self.in_exp_line:
            self.current_report_download_link = (
                "https://wlsy.sau.edu.cn/" + attrs["href"]
            )

        if tag == "td" and self.in_exp_line:
            self.parse_stage = self.parse_stage.next_stage()

        if (
            tag == "tr" and
            attrs.get("class", self._NULL_SENTINEL) == "STYLE1" and
            self.in_exp_table
        ):
            self.in_exp_line = True

        if (
            tag == "table" and
            attrs.get("class", self._NULL_SENTINEL) == "layui-table" and
            attrs.get("lay-size", self._NULL_SENTINEL) == "lg" and
            # since its value is indeed None, we must use another sentinel
            attrs.get("lay-even", self._NULL_SENTINEL) is None
        ):
            self.in_exp_table = True

    def handle_endtag(self, tag):
        if tag == "table" and self.in_exp_table:
            self.in_exp_table = False

        if tag == "tr" and self.in_exp_line:
            self.in_exp_line = False
            self.parse_stage = ExpViewHTMLParseStage.NONE
            self.parsed_classes.append(
                ChosenClass(
                    self.current_name,
                    self.current_teacher,
                    TimeTuple(*self.current_time.split('-')),
                    self.current_place,
                    self.current_seat or "还没有分配座位",
                    self.current_report_download_link
                )
            )
            self.current_name = ""
            self.current_teacher = ""
            self.current_time = ""
            self.current_place = ""
            self.current_seat = ""
            self.current_report_download_link = ""

    def handle_data(self, data):
        match self.parse_stage:
            case ExpViewHTMLParseStage.NAME:
                self.current_name += data.strip()

            case ExpViewHTMLParseStage.TEACHER:
                self.current_teacher += data.strip()

            case ExpViewHTMLParseStage.TIME:
                self.current_time += data.strip()

            case ExpViewHTMLParseStage.PLACE:
                self.current_place += data.strip()

            case ExpViewHTMLParseStage.SEAT:
                self.current_seat += data.strip()

def reload():
    pass

view_class_toplevel = tkinter.Toplevel(globals_module.root)
view_class_toplevel.wm_withdraw()

refresh_button = tkinter.ttk.Button(
    view_class_toplevel,
    text="刷新",
    command=refresh
)
