import importlib.resources
import textwrap
import tkinter
import tkinter.font
import tkinter.ttk

from . import globals as globals_module

current_activater_master = None

def activate_self(master):
    global current_activater_master
    current_activater_master = master

    about_toplevel.wm_transient(master)
    about_toplevel.wm_deiconify()

def activate_license_toplevel():
    about_license_toplevel.wm_transient(current_activater_master)
    about_license_toplevel.wm_deiconify()

about_toplevel = tkinter.Toplevel(globals_module.root)
about_toplevel.wm_title("关于 - 物理实验选课系统")
about_toplevel.wm_withdraw()
about_toplevel.wm_protocol("WM_DELETE_WINDOW", about_toplevel.wm_withdraw)

about_title = tkinter.ttk.Label(
    about_toplevel,
    anchor=tkinter.CENTER,
    text="沈航物理实验选课程序",
    font=tkinter.font.Font(about_toplevel, size=16)
)
about_version = tkinter.ttk.Label(
    about_toplevel,
    anchor=tkinter.CENTER,
    text=f"版本 {globals_module.VERSION}"
)
about_author = tkinter.ttk.Label(
    about_toplevel,
    anchor=tkinter.CENTER,
    text="By xiaoxi-ij478"
)
about_homepage = tkinter.ttk.Label(
    about_toplevel,
    anchor=tkinter.CENTER,
    text="项目主页：https://github.com/xiaoxi-ij478/sau-wlsy"
)
about_license_label = tkinter.ttk.Label(
    about_toplevel,
    anchor=tkinter.CENTER,
    text=textwrap.dedent("""\
        版权所有 (C) 2025 xiaoxi-ij478
        本程序以 GPL v3 授权。
    """)
)
about_view_full_license = tkinter.ttk.Button(
    about_toplevel,
    text="查看完整许可说明及许可"
)
about_close = tkinter.ttk.Button(
    about_toplevel,
    text="关闭",
    command=about_toplevel.wm_withdraw
)

about_license_toplevel = tkinter.Toplevel(about_toplevel)
about_license_toplevel.wm_withdraw()
about_license_toplevel.wm_title("关于 - 物理实验选课系统")
about_license_toplevel.wm_protocol(
    "WM_DELETE_WINDOW",
    about_license_toplevel.wm_withdraw
)

about_license_info_label = tkinter.ttk.Label(
    about_license_toplevel,
    wraplength=80,
    text=
    "This program is free software: you can redistribute it and/or modify "
    "it under the terms of the GNU General Public License as published by "
    "the Free Software Foundation, either version 3 of the License, or "
    "(at your option) any later version."
    "\n"
    "This program is distributed in the hope that it will be useful, "
    "but WITHOUT ANY WARRANTY; without even the implied warranty of "
    "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the "
    "GNU General Public License for more details."
    "\n"
    "You should have received a copy of the GNU General Public License "
    "along with this program.  If not, see <https://www.gnu.org/licenses/>. "
)
about_license_text_frame = tkinter.ttk.Frame(about_license_toplevel)
about_license_text = tkinter.Text(about_license_text_frame)

try:
    license_text = importlib.resources.files(globals_module).joinpath("LICENSE").read_text()
except (FileNotFoundError, PermissionError, OSError):
    license_text = textwrap.dedent("""
        我没有找到许可证文件！
        虽然我不会因此禁止使用程序，但你最好在重新分发程序时携带许可证文件。
    """)

about_license_text.insert(tkinter.END, license_text)
about_license_text.configure(state=tkinter.DISABLED)
about_license_text_scrollbar = tkinter.ttk.Scrollbar(about_license_text_frame)
about_license_close = tkinter.ttk.Button(
    about_license_toplevel,
    text="关闭",
    command=about_license_toplevel.wm_withdraw
)
about_license_text_scrollbar.configure(command=about_license_text.yview)
about_license_text.configure(yscrollcommand=about_license_text_scrollbar.set)

about_view_full_license.configure(command=activate_license_toplevel)
about_license_text.grid(row=0, column=0, sticky=tkinter.NSEW)
about_license_text_scrollbar.grid(row=0, column=1, sticky=tkinter.NSEW)
about_license_text_frame.rowconfigure(tkinter.ALL, weight=1)
about_license_text_frame.columnconfigure(tkinter.ALL, weight=1)
# ensure scroll bar would not expand
about_license_text_frame.columnconfigure(1, weight=0)

about_license_info_label.grid(row=0, column=0, sticky=tkinter.NSEW, padx=10, pady=10)
about_license_text_frame.grid(row=1, column=0, sticky=tkinter.NSEW, padx=10, pady=10)
about_license_close.grid(row=2, column=0, sticky=tkinter.NSEW, padx=10, pady=10)
about_license_toplevel.rowconfigure(tkinter.ALL, weight=1)
about_license_toplevel.columnconfigure(tkinter.ALL, weight=1)
about_license_toplevel.rowconfigure(0, weight=1)
about_license_toplevel.rowconfigure(2, weight=0)

about_title.grid(row=0, column=0, sticky=tkinter.NSEW, padx=10, pady=10)
about_version.grid(row=1, column=0, sticky=tkinter.NSEW, padx=10, pady=10)
about_author.grid(row=2, column=0, sticky=tkinter.NSEW, padx=10, pady=10)
about_homepage.grid(row=3, column=0, sticky=tkinter.NSEW, padx=10, pady=10)
about_license_label.grid(row=4, column=0, sticky=tkinter.NSEW, padx=10, pady=10)
about_view_full_license.grid(row=5, column=0, sticky=tkinter.NSEW, padx=10, pady=10)
about_close.grid(row=6, column=0, sticky=tkinter.NSEW, padx=10, pady=10)
about_toplevel.rowconfigure(tkinter.ALL, weight=1)
about_toplevel.columnconfigure(tkinter.ALL, weight=1)

globals_module.about_activate.add(activate_self)
