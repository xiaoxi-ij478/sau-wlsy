import csv
import itertools

## Refused Time Part ##

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

refused_times = []

def read_class_csv(filename):
    refused_times.clear()

    with open(filename, newline='') as fp:
        reader = iter(csv.reader(fp))

        itertools.dropwhile(lambda i: i[0] != "课程名称", reader)
        next(reader) # skip the header

        for i in reader:
            for j in i[6].split('、'):
                if '-' not in j:
                    refused_times.append(TimeTuple(int(i[1]), int(i[2]), int(i[6])))

                else:
                    if j.count('-') != 1:
                        tkinter.messagebox.showerror(
                            "错误",
                            "课程周数不合法；格式应为 <开始>-<结束>；\n"
                            f"实际为 '{j}'"
                        )
                        return

                    begin, end = j.split('-')
                    begin = int(begin)
                    end = int(end) + 1
                    if begin > end:
                        tkinter.messagebox.showerror(
                            "错误",
                            "课程周数不合法；开始应小于等于结束；\n"
                            f"实际为 '{j}'"
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

def filter_refused_times(aclass):
    return aclass.time not in refused_times

## Refused Teachers Part ##

refused_teachers = []

def filter_refused_teacher(aclass):
    return aclass.teacher not in refused_teachers

## Allowed Teachers Part ##

allowed_teachers = []

def filter_allowed_teacher(aclass):
    return aclass.teacher in allowed_teachers

## Keyword Part ##

allowed_keywords = []

def filter_keyword(aclass):
    return any(keyword in aclass.name for keyword in allowed_keywords)
