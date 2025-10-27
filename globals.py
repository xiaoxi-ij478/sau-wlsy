import tkinter
import tkinter.messagebox
import urllib.request

from . import util

def exit_exec():
    if tkinter.messagebox.askquestion("退出", "你确认要退出吗？") != tkinter.messagebox.YES:
        return

    root.destroy()

items_pre_page = 3
logon_user = ""
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
root = tkinter.Tk()
login_callback = util.CallbackCaller()
logout_callback = util.CallbackCaller()
exit_func = util.CallbackCaller()
login_activate = util.CallbackCaller()
nav_activate = util.CallbackCaller()
select_class_activate = util.CallbackCaller()
view_class_activate = util.CallbackCaller()
timetable_done = util.CallbackCaller()

exit_func.add(exit_exec)
