from PIL import ImageGrab
from win32api import GetSystemMetrics

from src.ui.DraggableRect import DraggableRect
from src.ui.MainUI import MainUI


def grab():
    x = rect.winfo_x()
    y = rect.winfo_y()
    width = rect.winfo_width()
    height = rect.winfo_height()

    pic = ImageGrab.grab(bbox=(x, y, x + width, y + height))
    pic.show()
    pic.save('./pic.png')


ui = MainUI(debug_mode=True)
root = ui.create_window()
ui.add_button(root.destroy, GetSystemMetrics(0)/2, 20, text='退出')


draggable_rect = DraggableRect(root, 20, 20, 200, 150)
rect = draggable_rect.create()
ui.set_click_through(rect.winfo_id())

ui.add_button(grab, GetSystemMetrics(0)/2, 50, text='截图')

root.mainloop()