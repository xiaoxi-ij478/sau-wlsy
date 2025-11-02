import csv
import itertools
import json
import tkinter.messagebox

from . import globals as globals_module
from . import util

## Refused Time Part ##

# shamelessly use format from Lemon Timetable
# 【使用说明】请在电脑上使用Excel软件编辑，并按照数据格式要求录入课程表。,,,,,,
# 【注意事项】表格的标题栏必须保留并且不要修改标题的名字，本模版的使用说明部分的文字可以保留也可以删除掉。以下字段说明中的必填字段必须包含，否者会作为无效条目。,,,,,,
# 【课程名称】[必填] 课程名称不要太长，不然在课程表里可能展示不完整。,,,,,,
# 【星期】[必填] 课程在周几上课，比如周一周二上课：1、2。,,,,,,
# 【开始节数】[必填] 当日该项课程第几节开始上课，必须为数字。,,,,,,
# 【结束节数】[必填] 当日该项课程上到第几节课结束，必须为数字。 比如 「高等数学」 第2节开始上课，上到第3节结束，共两节课。,,,,,,
# 【老师】[选填] 上课老师。,,,,,,
# 【地点】[选填] 上课地点。,,,,,,
# 【周数】[选填] 该课程在本学期的第几周上课，默认为全部周。,,,,,,
# 课程名称,星期,开始节数,结束节数,老师,地点,周数
# 高等数学,1,2,3,李老师,3教301,1-5、7-11单、12-16双
# 线性代数,2,3,4,李老师,3教301,1-16
# 大学英语,3,3,4,李老师,3教301,2、5、8
# we use only these columns:
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

refused_times = []

def read_class_csv(filename):
    refused_times.clear()

    with open(filename, newline='') as fp:
        reader = iter(csv.reader(fp))

        it = itertools.dropwhile(lambda i: i[0] != "课程名称", reader)
        next(it)

        for i in it:
            for j in i[6].split('、'):
                if '-' not in j:
                    refused_times.append(
                        util.TimeTuple(int(i[1]), int(i[2]), int(j))
                    )

                else:
                    if j.count('-') != 1:
                        tkinter.messagebox.showerror(
                            None,
                            "课程周数不合法；格式应为 <开始>-<结束>；\n"
                            f"实际为 '{j}'",
                            master=globals_module.root
                        )
                        return

                    begin, end = j.split('-')
                    begin = int(begin)
                    step = 1
                    if end[-1] == '单':
                        end = end[:-1]
                        if not begin % 2: # 6-11 for example
                            begin += 1
                        step = 2
                    elif end[-1] == '双':
                        end = end[:-1]
                        if begin % 2: # 7-12 for example
                            begin += 1
                        step = 2

                    end = int(end) + 1
                    if begin > end:
                        tkinter.messagebox.showerror(
                            None,
                            "课程周数不合法；开始应小于等于结束；\n"
                            f"实际为 '{j}'",
                            master=globals_module.root
                        )
                        return

                    for week in range(begin, end, step):
                        refused_times.append(
                            util.TimeTuple(int(i[1]), int(i[2]), week)
                        )

    tkinter.messagebox.showinfo(
        None,
        "课程表加载完成",
        master=globals_module.root
    )
    globals_module.timetable_done()

# json format:

##def read_class_json(filename):
##    with open(filename) as fp:
##        data = json.load(fp)
##
##    for i in reader:
##        for j in i[6].split('、'):
##            if '-' not in j:
##                refused_times.append(
##                    util.TimeTuple(int(i[1]), int(i[2]), int(i[6]))
##                )
##
##            else:
##                if j.count('-') != 1:
##                    tkinter.messagebox.showerror(
##                        "错误",
##                        "课程周数不合法；格式应为 <开始>-<结束>；\n"
##                        f"实际为 '{j}'",
##                        master=globals_module.root
##                    )
##                    return
##
##                begin, end = j.split('-')
##                begin = int(begin)
##                end = int(end) + 1
##                if begin > end:
##                    tkinter.messagebox.showerror(
##                        "错误",
##                        "课程周数不合法；开始应小于等于结束；\n"
##                        f"实际为 '{j}'",
##                        master=globals_module.root
##                    )
##                    return
##
##                step = 1
##                if end[-1] == '单':
##                    if not begin % 2: # 6-11 for example
##                        begin += 1
##                    step = 2
##                elif end[-1] == '双':
##                    if begin % 2: # 7-12 for example
##                        begin += 1
##                    step = 2
##
##                for week in range(begin, end, step):
##                    refused_times.append(
##                        util.TimeTuple(int(i[1]), int(i[2]), week)
##                    )
##
##    tkinter.messagebox.showinfo(
##        "加载完成",
##        "课程表加载完成",
##        master=globals_module.root
##    )
##    globals_module.timetable_done()
##

def filter_refused_times(aclass):
    if aclass.name.endswith("4学时"):
        # 4 time mapping:
        # 1, 2 -> 1
        # 3, 4 -> 2
        # 5, 6, 7, 8 -> 3
        for t, et in (
            (1, (1, 2)),
            (2, (3, 4)),
            (3, (5, 6, 7, 8))
        ):
            if aclass.time.class_time == t:
                exact_time = [
                    util.TimeTuple(
                        aclass.time.week,
                        aclass.time.day_of_week,
                        i
                    ) for i in et
                ]
                break

        return all(i not in refused_times for i in exact_time)

    else:
        return aclass.time not in refused_times if refused_times else True

## Refused Teachers Part ##

refused_teachers = []

def filter_refused_teacher(aclass):
    return aclass.teacher not in refused_teachers if refused_teachers else True

## Allowed Teachers Part ##

allowed_teachers = []

def filter_allowed_teacher(aclass):
    return aclass.teacher in allowed_teachers if allowed_teachers else True

## Keyword Part ##

filtered_keyword = []

def filter_keyword(aclass):
    return (
        any(keyword in aclass.name for keyword in filtered_keyword)
        if filtered_keyword
        else True
    )
