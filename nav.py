import tkinter
import tkinter.messagebox
import tkinter.ttk

import globals as globals_module

def logon_callback():
    login_label_str.set(f"已登录为: {globals_module.logon_user}")

def select_class_activate():
    nav_frame.wm_withdraw()
    globals_module.select_class_activate()

def view_selected_activate():
    nav_frame.wm_withdraw()
    globals_module.view_selected_activate()

def remove_class_activate():
    nav_frame.wm_withdraw()
    globals_module.remove_class_activate()

def score_check_activate():
    nav_frame.wm_withdraw()
    globals_module.score_check_activate()

def logout_activate():
    if not tkinter.messagebox.askquestion("退出", "你确认要退出吗？"):
        return

    nav_frame.wm_withdraw()
    globals_module.login_activate()

nav_toplevel = tkinter.Toplevel(globals_module.root)

login_label_str = tkinter.StringVar(nav_frame, "已登录为: ")
login_label = tkinter.ttk.Label(nav_frame, textvariable=login_label_str)

select_class_button = tkinter.ttk.Button(nav_frame, text="选课")
view_selected_button = tkinter.ttk.Button(nav_frame, text="查看已选")
remove_class_button = tkinter.ttk.Button(nav_frame, text="取消选课")
score_check_button = tkinter.ttk.Button(nav_frame, text="查看成绩")
logout_button = tkinter.ttk.Button(nav_frame, text="退出")

login_label.grid(row=0, column=0, sticky=tkinter.NSEW, padx=10, pady=10)
select_class_button.grid(row=1, column=0, sticky=tkinter.NSEW, padx=10, pady=10)
view_selected_button.grid(row=1, column=0, sticky=tkinter.NSEW, padx=10, pady=10)
remove_class_button.grid(row=1, column=0, sticky=tkinter.NSEW, padx=10, pady=10)
score_check_button.grid(row=1, column=0, sticky=tkinter.NSEW, padx=10, pady=10)
logout_button.grid(row=1, column=0, sticky=tkinter.NSEW, padx=10, pady=10)

nav_frame.rowconfigure(tkinter.ALL, weight=1)
nav_frame.columnconfigure(tkinter.ALL, weight=1)

globals_module.nav_activate.add(nav_toplevel.wm_deiconify)
