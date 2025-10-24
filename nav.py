import tkinter
import tkinter.messagebox
import tkinter.ttk

from . import about
from . import globals as globals_module

def logon_callback():
    login_label_str.set(f"已登录为: {globals_module.logon_user}")

def select_class_activate():
    nav_toplevel.wm_withdraw()
    globals_module.select_class_activate()

def view_class_activate():
    nav_toplevel.wm_withdraw()
    globals_module.view_class_activate()

def logout_activate():
    if tkinter.messagebox.askquestion("登出", "你确认要登出吗？") != tkinter.messagebox.YES:
        return

    nav_toplevel.wm_withdraw()
    globals_module.login_activate()

nav_toplevel = tkinter.Toplevel(globals_module.root)
nav_toplevel.wm_title("导航 - 物理实验选课系统")
nav_toplevel.wm_withdraw()
nav_toplevel.wm_protocol("WM_DELETE_WINDOW", globals_module.exit_func)

nav_menu = tkinter.Menu(nav_toplevel, tearoff=False)
nav_menu.add_command(label="退出", command=globals_module.exit_func)
nav_menu.add_command(label="关于", command=about.about_toplevel.wm_deiconify)

nav_toplevel.configure(menu=nav_menu)

login_label_str = tkinter.StringVar(nav_toplevel, "已登录为: ")
login_label = tkinter.ttk.Label(
    nav_toplevel,
    textvariable=login_label_str,
    anchor=tkinter.CENTER
)

select_class_button = tkinter.ttk.Button(nav_toplevel, text="选课", command=select_class_activate)
view_class_button = tkinter.ttk.Button(nav_toplevel, text="查看课程", command=view_class_activate)
logout_button = tkinter.ttk.Button(nav_toplevel, text="登出", command=logout_activate)

login_label.grid(row=0, column=0, sticky=tkinter.NSEW, padx=10, pady=10)
select_class_button.grid(row=1, column=0, sticky=tkinter.NSEW, padx=10, pady=10)
view_class_button.grid(row=2, column=0, sticky=tkinter.NSEW, padx=10, pady=10)
logout_button.grid(row=3, column=0, sticky=tkinter.NSEW, padx=10, pady=10)

nav_toplevel.rowconfigure(tkinter.ALL, weight=1)
nav_toplevel.columnconfigure(tkinter.ALL, weight=1)

globals_module.nav_activate.add(nav_toplevel.wm_deiconify)
globals_module.login_callback.add(nav_toplevel.wm_deiconify)
globals_module.login_callback.add(logon_callback)
