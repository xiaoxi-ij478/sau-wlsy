# do this on __init__ so it'll fail on every use
import tkinter
tkinter.NoDefaultRoot()

from . import about
from . import login
from . import nav
from . import select_class
from . import view_class
