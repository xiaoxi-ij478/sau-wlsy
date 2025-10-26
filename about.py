import tkinter
import tkinter.font
import tkinter.ttk

from . import globals as globals_module

about_toplevel = tkinter.Toplevel(globals_module.root)
about_toplevel.wm_withdraw()

about_title = tkinter.ttk.Label(
    about_toplevel,
    text="沈航物理实验选课程序",
    font=tkinter.font.Font(size=16)
)
about_author = tkinter.ttk.Label(
    about_toplevel,
    text="By xiaoxi-ij478"
)
about_homepage = tkinter.ttk.Label(
    about_toplevel,
    text="项目主页：https://github.com/xiaoxi-ij478/sau-wlsy"
)
about_close = tkinter.ttk.Button(
    about_toplevel,
    text="关闭",
    command=about_toplevel.wm_withdraw
)

about_title.grid(row=0, column=0, sticky=tkinter.NS, padx=10, pady=10)
about_author.grid(row=1, column=0, sticky=tkinter.NS, padx=10, pady=10)
about_homepage.grid(row=2, column=0, sticky=tkinter.NS, padx=10, pady=10)
about_close.grid(row=3, column=0, sticky=tkinter.NS, padx=10, pady=10)

about_toplevel.rowconfigure(tkinter.ALL, weight=1)
about_toplevel.columnconfigure(tkinter.ALL, weight=1)
