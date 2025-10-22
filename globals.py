import http.cookiejar
import tkinter
import urllib.request

cookiejar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookiejar))
root = tkinter.Tk()
logon_user = ""

class CallbackCaller:
    def __init__(self):
        self.callbacks = []

    def __call__(self, *args, **kwargs):
        for cb in self.callbacks:
            cb(*args, **kwargs)

    def add(self, callback):
        self.callbacks.append(callback)

login_callback = CallbackCaller()
logout_callback = CallbackCaller()
login_activate = CallbackCaller()
nav_activate = CallbackCaller()
select_class_activate = CallbackCaller()
view_selected_activate = CallbackCaller()
score_check_activate = CallbackCaller()
remove_class_activate = CallbackCaller()
