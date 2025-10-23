import tkinter
import tkinter.ttk

from . import globals as globals_module

def refresh():
    

view_class_toplevel = tkinter.Toplevel(globals_module.root)

refresh_button = tkinter.ttk.Button(
    view_class_toplevel,
    text="刷新",
    command=refresh
)
