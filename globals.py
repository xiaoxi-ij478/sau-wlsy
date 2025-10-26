import http.cookiejar
import tkinter
import tkinter.messagebox
import urllib.request

from . import util

def exit_exec():
    if tkinter.messagebox.askquestion("退出", "你确认要退出吗？") != tkinter.messagebox.YES:
        return

    root.destroy()

logon_user = ""
cookiejar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookiejar))

login_callback = util.CallbackCaller()
logout_callback = util.CallbackCaller()
exit_func = util.CallbackCaller()
login_activate = util.CallbackCaller()
nav_activate = util.CallbackCaller()
select_class_activate = util.CallbackCaller()
view_class_activate = util.CallbackCaller()

root = tkinter.Tk()

exit_func.add(exit_exec)
