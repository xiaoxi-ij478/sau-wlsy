import tkinter
import tkinter.messagebox
import urllib.request

from . import util

def logout():
    opener.open("https://wlsy.sau.edu.cn/physlab/logout.php")

def exit_exec():
    if tkinter.messagebox.askquestion(
        "退出",
        "你确认要退出吗？",
        master=root
    ) != tkinter.messagebox.YES:
        return

    logout()
    root.destroy()

items_pre_page = 2
logon_user = ""
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
root = tkinter.Tk()
login_callback = util.CallbackCaller()
logout_callback = util.CallbackCaller()
exit_func = util.CallbackCaller()
about_activate = util.CallbackCaller()
login_activate = util.CallbackCaller()
nav_activate = util.CallbackCaller()
select_class_activate = util.CallbackCaller()
view_class_activate = util.CallbackCaller()
timetable_done = util.CallbackCaller()

root.bind_class(
    "Label",
    "<Configure>",
    lambda event: event.widget.configure(wraplength=event.width),
    True
)
root.bind_class(
    "TLabel",
    "<Configure>",
    lambda event: event.widget.configure(wraplength=event.width),
    True
)

exit_func.add(exit_exec)
