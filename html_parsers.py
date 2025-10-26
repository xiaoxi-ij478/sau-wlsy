import enum
import html.parser

from . import util

# parser for https://wlsy.sau.edu.cn/physlab/stuyy_test2.php
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

    def _append_class(self):
        self.parsed_classes.append(
            util.AvailableClass(
                self.current_name,
                self.current_time,
                self.current_teacher,
                self.current_place,
                None,
                None,
                None,
                self.current_exp_post_id
            )
        )


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
                self._append_class()

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
                self._append_class()

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
            self.current_time = util.TimeTuple(
                *map(int, l[1].replace("时间：", '').split(' -'))
            )
            self.current_place = l[2].replace("地点：", '')

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

# parser for https://wlsy.sau.edu.cn/physlab/stuyycx.php
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
        self.parse_stage = ExpViewHTMLParseStage.NONE
        self.parsed_classes = []

    def _append_class(self):
        self.parsed_classes.append(
            util.ExpClass(
                self.current_name,
                util.TimeTuple(*map(int, self.current_time.split('-'))),
                self.current_teacher,
                self.current_place,
                int(self.current_seat) if self.current_seat else None,
                None,
                self.current_report_download_link
            )
        )        

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
            self._append_class()
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

class ExpScoreHTMLParseStage(enum.IntEnum):
    NONE = enum.auto()
    STU_NAME = enum.auto()
    NAME = enum.auto()
    TEACHER = enum.auto()
    SCORE = enum.auto()

    def next_stage(self):
        return type(self)(self + 1)

# parser for https://wlsy.sau.edu.cn/physlab/scjcx.php
class ExpScoreHTMLParser(html.parser.HTMLParser):
    _NULL_SENTINEL = object()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.current_name = ""
        self.current_teacher = ""
        self.current_score = ""
        self.in_exp_table = False
        self.in_exp_line = False
        self.parse_stage = ExpScoreHTMLParseStage.NONE
        self.parsed_classes = []

    def _append_class(self):
        self.parsed_classes.append(
            util.ExpClass(
                self.current_name,
                None,
                self.current_teacher,
                None,
                None,
                int(self.current_score) if self.current_score else None,
                None
            )
        )

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

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
            attrs.get("width", self._NULL_SENTINEL) == "95%" and
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
            self.parse_stage = ExpScoreHTMLParseStage.NONE
            
            self._append_class()
            self.current_name = ""
            self.current_teacher = ""
            self.current_score = ""

    def handle_data(self, data):
        match self.parse_stage:
            case ExpScoreHTMLParseStage.NAME:
                self.current_name += data.strip()

            case ExpScoreHTMLParseStage.TEACHER:
                self.current_teacher += data.strip()

            case ExpScoreHTMLParseStage.SCORE:
                self.current_score += data.strip()
