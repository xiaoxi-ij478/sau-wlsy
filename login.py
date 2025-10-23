import io
import tkinter
import tkinter.ttk
import urllib.parse

from . import about
from . import globals as globals_module
from . import util

def login(*args):
    with util.HoldContextManager(login_toplevel):
        notify_info.set("")

        reply = globals_module.opener.open(
            "https://wlsy.sau.edu.cn/note.php",
            urllib.parse.urlencode({
                "stu_id": username.get(),
                "stupwd": password.get(),
                "Submit": "确认提交"
            }).encode()
        ).read().decode()

        if "学号错误，请重新输入！" in reply:
            notify_info.set("学号错误")
            return

        if "用户密码错误，请重新登录！！！" in reply:
            notify_info.set("密码错误")
            return

        page_iter = iter(io.TextIOWrapper(globals_module.opener.open("https://wlsy.sau.edu.cn/physlab/s6.php")))
        real_username = username.get()
        while True:
            try:
                if "姓名：" in next(page_iter):
                    real_username = next(page_iter).replace("<td>", "").replace("</td>", "").strip()
                    break

            except StopIteration:
                break

        globals_module.logon_user = real_username
        login_toplevel.wm_withdraw()
        globals_module.login_callback()

# well, why not use root?
login_toplevel = globals_module.root
login_toplevel.wm_title("登录 - 物理实验选课系统")
login_toplevel.wm_withdraw()
login_toplevel.wm_protocol("WM_DELETE_WINDOW", globals_module.exit_func)

login_menu = tkinter.Menu(login_toplevel, tearoff=False)
login_menu.add_command(label="退出", command=globals_module.exit_func)
login_menu.add_command(label="关于", command=about.about_toplevel.wm_deiconify)

login_toplevel.configure(menu=login_menu)

username = tkinter.StringVar(login_toplevel)
username_label = tkinter.ttk.Label(login_toplevel, text="学号")
username_input = tkinter.ttk.Entry(login_toplevel, textvariable=username)

password = tkinter.StringVar(login_toplevel)
password_label = tkinter.ttk.Label(login_toplevel, text="密码")
password_input = tkinter.ttk.Entry(login_toplevel, textvariable=password, show='*')

notify_info = tkinter.StringVar(login_toplevel)
notify_label = tkinter.ttk.Label(login_toplevel, textvariable=notify_info)

login_button = tkinter.ttk.Button(
    login_toplevel,
    text="登录",
    command=lambda: login_toplevel.after(5, login),
    default=tkinter.ACTIVE
)

username_label.grid(row=0, column=0, sticky=tkinter.NSEW, padx=10)
username_input.grid(row=0, column=1, sticky=tkinter.NSEW, padx=10, pady=10)
password_label.grid(row=1, column=0, sticky=tkinter.NSEW, padx=10)
password_input.grid(row=1, column=1, sticky=tkinter.NSEW, padx=10, pady=10)
notify_label.grid(row=2, column=0, columnspan=2, sticky=tkinter.NS, padx=10, pady=10)
login_button.grid(row=3, column=0, columnspan=2, sticky=tkinter.NSEW, padx=10, pady=10)
login_toplevel.columnconfigure(tkinter.ALL, weight=1)
login_toplevel.rowconfigure(tkinter.ALL, weight=1)

login_toplevel.bind("<Return>", lambda: login_toplevel.after(5, login))

globals_module.login_activate.add(login_toplevel.wm_deiconify)
