from tkinter import *
from tkinter import ttk
import win32gui
import win32con
from win32api import GetSystemMetrics


class MainUI:
    debug_mode = False

    def __init__(self, debug_mode=False):
        self.root = None
        self.bg = None
        self.debug_mode = debug_mode

    def set_click_through(self, hwnd):
        # print("setting window properties")
        try:
            # todo warning need to be removed
            styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            # styles = win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, styles)
            win32gui.SetLayeredWindowAttributes(hwnd, 0, 255, win32con.LWA_ALPHA)
        except Exception as e:
            print(e)

    def create_window(self):
        # Dimensions
        width = GetSystemMetrics(0)
        height = GetSystemMetrics(1)

        root = Tk()
        root.wm_attributes('-fullscreen', 'True')
        root.geometry('%dx%d' % (width, height))
        root.title("Overlay")
        root.config(bg='white')

        root.attributes('-transparentcolor', 'white', '-topmost', 1)
        root.wm_attributes("-topmost", 1)

        self.root = root

        if self.debug_mode:
            bg = Canvas(root, width=width, height=height, bg='white')
        else:
            # highlightthickness will make the bolder away
            bg = Canvas(root, width=width, height=height, bg='white', highlightthickness=0)
        self.bg = bg

        self.set_click_through(bg.winfo_id())

        bg.pack()
        return root

    def add_button(self, command,  x, y, text='Button'):
        button = ttk.Button(self.root, text=text, command=command)
        self.bg.create_window(x, y, window=button)
        self.bg.pack()




