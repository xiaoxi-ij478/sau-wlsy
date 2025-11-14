import enum
import html.parser

from . import globals as globals_module
from . import util

# all the parsers are very fragile.
# DO NOT EXPECT THEM TO BE STABLE

class ExpSelectPageHTMLParser(html.parser.HTMLParser):
    "parser for https://wlsy.sau.edu.cn/physlab/stuyy_test2.php"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.parsed_at_least_one_class = False
        self.passed_name_tag = False
        self.parsed_extra_info = False
        self.in_name_tag = False
        self.in_exp_data_tag = False
        self.current_name = ""
        self.pending_data = ""
        self.current_post_id = 0
        self.parsed_classes = []

    def _append_class(self):
        l = [i.strip() for i in self.pending_data.split('\xA0') if i.strip()]
        current_teacher = l[0].replace("教师：", '')
        current_time = util.TimeTuple(
            *map(int, l[1].replace("时间：", '').split(' -'))
        )
        current_place = l[2].replace("地点：", '')

        self.parsed_classes.append(
            util.AvailableClass(
                self.current_name,
                current_time,
                current_teacher,
                current_place,
                self.current_post_id
            )
        )
        self.pending_data = ""

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        if (
            self.in_exp_data_tag and
            tag == "input" and
            attrs.get("type", None) == "radio" and
            attrs.get("name", None) == "sy_sy" and
            attrs.get("class", None) == "body"
        ):
            if self.passed_name_tag:
                self.parsed_extra_info = False
                self.passed_name_tag = False
                self._append_class()

            self.parsed_at_least_one_class = True
            self.current_post_id = int(attrs["value"])

        if tag == "font" and self.in_exp_data_tag:
            self.in_name_tag = True

        if (
            tag == "form" and
            attrs == {"method": "POST", "action": "stuyy_test2.php"}
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

        if self.passed_name_tag:
            self.pending_data += data

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
    "parser for https://wlsy.sau.edu.cn/physlab/stuyycx.php"
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
            util.ChosenClass(
                self.current_name,
                util.TimeTuple(*map(int, self.current_time.split('-'))),
                self.current_teacher,
                self.current_place,
                int(self.current_seat) if self.current_seat else None,
                None,
                self.current_report_download_link,
                False,
                None
            )
        )

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        if tag == "a" and self.in_exp_line:
            self.current_report_download_link = (
                f"{globals_module.WLSY_HOST}/physlab/" + attrs["href"]
            )

        if tag == "td" and self.in_exp_line:
            self.parse_stage = self.parse_stage.next_stage()

        if tag == "tr" and attrs == {"class": "STYLE1"} and self.in_exp_table:
            self.in_exp_line = True

        if (
            tag == "table" and
            attrs == {"class": "layui-table", "lay-size": "lg", "lay-even": None}
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

class ExpScoreHTMLParser(html.parser.HTMLParser):
    "parser for https://wlsy.sau.edu.cn/physlab/scjcx.php"
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
            util.ChosenClass(
                self.current_name,
                None,
                self.current_teacher,
                None,
                None,
                int(self.current_score) if self.current_score else None,
                None,
                False,
                None
            )
        )

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        if tag == "td" and self.in_exp_line:
            self.parse_stage = self.parse_stage.next_stage()

        if tag == "tr" and attrs == {"class": "STYLE1"} and self.in_exp_table:
            self.in_exp_line = True

        if (
            tag == "table" and
            attrs == {
                "width": "95%",
                "class": "layui-table",
                "lay-size": "lg",
                "lay-even": None
            }
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

class ExpCancelHTMLParseStage(enum.IntEnum):
    NONE = enum.auto()
    NAME = enum.auto()
    TIME = enum.auto()

    def next_stage(self):
        return type(self)(self + 1)

class ExpCancelHTMLParser(html.parser.HTMLParser):
    "parser for https://wlsy.sau.edu.cn/physlab/stuqxyy.php"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cancel_times = 0
        self.current_name = ""
        self.current_time = ""
        self.current_post_id = 0
        self.passed_pre_cancel_times_tag = False
        self.passed_cancel_times = False
        self.in_cancel_exp_item = False
        self.in_cancel_exp_inner_item = False
        self.next_should_parse_item = False
        self.parse_stage = ExpCancelHTMLParseStage.NONE
        self.parsed_classes = []

    def _append_class(self):
        self.parsed_classes.append(
            util.ChosenClass(
                self.current_name,
                util.TimeTuple(
                    *map(int, self.current_time.replace(' ', '').split('-'))
                ),
                None,
                None,
                None,
                None,
                None,
                True,
                self.current_post_id
            )
        )

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        if (
            tag == "span" and
            attrs == {"style": "font-weight: bold"} and
            self.in_cancel_exp_inner_item
        ):
            self.next_should_parse_item = True

        if (
            tag == "input" and
            attrs.get("type", None) == "radio" and
            attrs.get("name", None) == "sy_qx" and
            self.in_cancel_exp_item
        ):
            self.current_post_id = int(attrs["value"])

        if (
            tag == "div" and
            attrs == {
                "class": "layui-input-block",
                "style": "margin-left: 0; padding: 10px 0 0 30px;"
            } and
            self.in_cancel_exp_item
        ):
            self.in_cancel_exp_inner_item = True

        if tag == "div" and attrs == {"class": "experiment-item"}:
            self.in_cancel_exp_item = True

    def handle_endtag(self, tag):
        if tag == "span" and self.next_should_parse_item:
            self.parse_stage = self.parse_stage.next_stage()
            self.next_should_parse_item = False

        if tag == "strong" and not self.passed_cancel_times:
            self.passed_pre_cancel_times_tag = True

        if tag == "div" and self.in_cancel_exp_inner_item:
            self.in_cancel_exp_inner_item = False

        if tag == "div" and self.in_cancel_exp_item:
            self.in_cancel_exp_item = False
            self._append_class()

    def handle_data(self, data):
        if self.passed_pre_cancel_times_tag and not self.passed_cancel_times:
            self.cancel_times = int(data[-1])
            self.passed_cancel_times = True
            return

        if not self.next_should_parse_item:
            match self.parse_stage:
                case ExpCancelHTMLParseStage.NAME:
                    self.current_name += data.strip()

                case ExpCancelHTMLParseStage.TIME:
                    self.current_time += data.strip()

class ExpSelectResultHTMLParser(html.parser.HTMLParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.test_next_is_p_tag = False
        self.next_is_notif_data = False
        self.next_is_script_data = False
        self.notif_data = ""
        # sometimes the html does not contain notification info
        # so we assume it failed when not notified
        self.success = False

    def handle_starttag(self, tag, attrs):
        if tag == "p" and self.test_next_is_p_tag:
            self.test_next_is_p_tag = False
            self.next_is_notif_data = True

        if tag == "script":
            self.next_is_script_data = True

    def handle_endtag(self, tag):
        if tag == "script":
            self.next_is_script_data = False

    def handle_data(self, data):
        if (
            self.next_is_script_data and
            "                    layer.msg('" in data and
            "',{icon:" in data and
            "});" in data
        ):
            # XXX there're no much chance to try all the possible situations,
            # XXX so these are just guesses
            # XXX I'll refactor them as I gather more data

            if "icon:2" in data:
                self.success = False
            elif "icon:1" in data:
                self.success = True

        if self.next_is_notif_data:
            self.notif_data = data
            self.next_is_notif_data = False

        if " \xA0\xA0\xA0\xA0实验指导教师：" in data:
            self.test_next_is_p_tag = True
