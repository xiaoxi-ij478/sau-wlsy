import contextlib
import io
import os.path
import tkinter
import tkinter.ttk
import urllib.parse

from . import about
from . import globals as globals_module
from . import util

def login(*args):
    with util.HoldWindowContext(login_toplevel):
        notify_info.set("")

        reply = io.TextIOWrapper(
            globals_module.opener.open(
                f"{globals_module.WLSY_HOST}/note.php",
                urllib.parse.urlencode({
                    "stu_id": username.get(),
                    "stupwd": password.get(),
                    "Submit": "确认提交"
                }).encode()
            )
        )

        for line in reply:
            if "学号错误，请重新输入！" in line:
                notify_info.set("学号错误")
                return

            if "用户密码错误，请重新登录！！！" in line:
                notify_info.set("密码错误")
                return

        page = io.TextIOWrapper(
            globals_module.opener.open(
                f"{globals_module.WLSY_HOST}/physlab/s6.php"
            )
        )
        real_username = username.get()
        next_is_real_username = False

        for line in page:
            if next_is_real_username:
                real_username = line.replace("<td>", "").replace("</td>", "").strip()
                break

            if "姓名：" in line:
                next_is_real_username = True
                continue

        globals_module.logon_user = real_username
        login_toplevel.wm_withdraw()
        globals_module.login_callback()

def load_password():
    with contextlib.suppress(FileNotFoundError, PermissionError, OSError):
        with open(os.path.join(os.path.expanduser("~"), ".wlsyrc")) as f:
            username.set(f.readline().strip())
            password.set(f.readline().strip())

def save_password():
    if not save_password_var.get():
        return

    with contextlib.suppress(FileNotFoundError, PermissionError, OSError):
        with open(os.path.join(os.path.expanduser("~"), ".wlsyrc"), "w") as f:
            print(username.get(), file=f)
            print(password.get(), file=f)

# well, why not use root?
login_toplevel = globals_module.root
login_toplevel.wm_title("登录 - 物理实验选课系统")
login_toplevel.wm_withdraw()
login_toplevel.wm_protocol("WM_DELETE_WINDOW", globals_module.exit_func)

login_menu = tkinter.Menu(login_toplevel, tearoff=False)
login_menu.add_command(label="退出", command=globals_module.exit_func)
login_menu.add_command(
    label="关于",
    command=lambda: globals_module.about_activate(login_toplevel)
)

title_label = tkinter.ttk.Label(
    login_toplevel,
    text="登录",
    anchor=tkinter.CENTER,
    font=tkinter.font.Font(login_toplevel, size=16)
)

username = tkinter.StringVar(login_toplevel)
username_label = tkinter.ttk.Label(login_toplevel, text="学号")
username_input = tkinter.ttk.Entry(login_toplevel, textvariable=username)

password = tkinter.StringVar(login_toplevel)
password_label = tkinter.ttk.Label(login_toplevel, text="密码")
password_input = tkinter.ttk.Entry(login_toplevel, textvariable=password, show='*')

save_password_var = tkinter.BooleanVar(login_toplevel)
save_password_checkbox = tkinter.ttk.Checkbutton(
    login_toplevel,
    text="保存密码",
    variable=save_password_var
)

notify_info = tkinter.StringVar(login_toplevel)
notify_label = tkinter.ttk.Label(
    login_toplevel,
    textvariable=notify_info,
    anchor=tkinter.CENTER
)

login_button = tkinter.ttk.Button(
    login_toplevel,
    text="登录",
    command=login,
    default=tkinter.ACTIVE
)

login_toplevel.configure(menu=login_menu)

title_label.grid(row=0, column=0, columnspan=2, sticky=tkinter.NSEW, padx=10, pady=10)
username_label.grid(row=1, column=0, sticky=tkinter.NSEW, padx=10)
username_input.grid(row=1, column=1, sticky=tkinter.NSEW, padx=10, pady=10)
password_label.grid(row=2, column=0, sticky=tkinter.NSEW, padx=10)
password_input.grid(row=2, column=1, sticky=tkinter.NSEW, padx=10, pady=10)
save_password_checkbox.grid(row=3, column=0, columnspan=2, sticky=tkinter.NSEW, padx=10, pady=10)
notify_label.grid(row=4, column=0, columnspan=2, sticky=tkinter.NSEW, padx=10, pady=10)
login_button.grid(row=5, column=0, columnspan=2, sticky=tkinter.NSEW, padx=10, pady=10)
login_toplevel.columnconfigure(tkinter.ALL, weight=1)
login_toplevel.rowconfigure(tkinter.ALL, weight=1)

login_toplevel.bind("<Return>", login)
load_password()

globals_module.login_callback.add(save_password)
globals_module.login_activate.add(login_toplevel.wm_deiconify)
