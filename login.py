import tkinter
import tkinter.ttk
import urllib.parse

import globals as globals_module

def login(username, password):
    notify_info.set("")

    reply = globals_module.opener.open(
        "https://wlsy.sau.edu.cn/note.php",
        urllib.parse.urlencode({
            "stu_id": username,
            "stupwd": password,
            "Submit": "确认提交"
        })
    ).read()

    if "用户密码错误，请重新登录！！！" in reply:
        notify_info.set("用户名或密码错误")
        return

    page_iter = iter(globals_module.opener.open("https://wlsy.sau.edu.cn/physlab/s6.php"))
    real_username = username
    while True:
        try:
            if "姓名：" in next(page_iter):
                real_username = next(page_iter).replace("<td>", "").replace("</td>", "").strip()
            break
        except StopIteration:
            break

    globals_module.logon_user = real_username
    globals_module.login_callback()

login_toplevel = tkinter.Toplevel(globals_module.root)

username_label = tkinter.ttk.Label(login_frame, text="学号")
username = tkinter.StringVar(login_frame)
username_input = tkinter.ttk.Entry(login_frame, textvariable=username)

password_label = tkinter.ttk.Label(login_frame, text="密码")
password = tkinter.StringVar(login_frame)
password_input = tkinter.ttk.Entry(login_frame, textvariable=password, show='*')

notify_info = tkinter.StringVar(login_frame)
notify_label = tkinter.ttk.Label(login_frame, textvariable=notify_info)

login_button = tkinter.ttk.Button(login_frame, text="登录", command=login)

username_label.grid(row=0, column=0, sticky=tkinter.NSEW, padx=10)
username_input.grid(row=0, column=1, sticky=tkinter.NSEW, padx=10, pady=10)
password_label.grid(row=1, column=0, sticky=tkinter.NSEW, padx=10)
password_input.grid(row=1, column=1, sticky=tkinter.NSEW, padx=10, pady=10)
notify_label.grid(row=2, column=0, columnspan=2, sticky=tkinter.NSEW, padx=10, pady=10)
login_button.grid(row=3, column=0, columnspan=2, sticky=tkinter.NSEW, padx=10, pady=10)
login_frame.columnconfigure(tkinter.ALL, weight=1)
login_frame.rowconfigure(tkinter.ALL, weight=1)

globals_module.login_activate.add(login_toplevel.wm_deiconify)
