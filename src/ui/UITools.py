# https://blog.csdn.net/qfcy_/article/details/122615118
import tkinter as tk
import tkinter.ttk as ttk
from ctypes import *

__version__ = "1.1.2"


class _PointAPI(Structure):  # 用于getpos()中API函数的调用
    _fields_ = [("x", c_ulong), ("y", c_ulong)]


def getpos():
    # 调用API函数获取当前鼠标位置。返回值以(x,y)形式表示。
    po = _PointAPI()
    windll.user32.GetCursorPos(byref(po))
    return int(po.x), int(po.y)


def xpos(): return getpos()[0]


def ypos(): return getpos()[1]


# tkinter控件支持作为字典键。
# bound的键是dragger, 值是包含1个或多个绑定事件的列表, 值用于存储控件绑定的数据
# 列表的一项是对应tkwidget和其他信息的元组
bound = {}


def __add(wid, data):  # 添加绑定数据
    bound[wid] = bound.get(wid, []) + [data]


def __remove(wid, key):  # 用于从bound中移除绑定
    for i in range(len(bound[wid])):
        try:
            if bound[wid][i][0] == key:
                del bound[wid][i]
        except IndexError:
            pass


def __get(wid, key=''):  # 用于从bound中获取绑定数据
    if not key: return bound[wid][0]
    if key == 'resize':
        for i in range(len(bound[wid])):
            for s in 'nwse':
                if s in bound[wid][i][0].lower():
                    return bound[wid][i]
    for i in range(len(bound[wid])):
        if bound[wid][i][0] == key:
            return bound[wid][i]


def move(widget, x=None, y=None, width=None, height=None):
    "移动控件或窗口widget, 参数皆可选。"
    x = x if x != None else widget.winfo_x()
    y = y if y != None else widget.winfo_y()
    width = width if width != None else widget.winfo_width()
    height = height if height != None else widget.winfo_height()
    if isinstance(widget, tk.Wm):
        widget.geometry("%dx%d+%d+%d" % (width, height, x, y))
    else:
        widget.place(x=x, y=y, width=width, height=height)
    return x, y, width, height


def _mousedown(event):
    if event.widget not in bound: return
    lst = bound[event.widget]
    for data in lst:  # 开始拖动时, 在每一个控件记录位置和控件尺寸
        widget = data[1]
        widget.mousex, widget.mousey = getpos()
        widget.startx, widget.starty = widget.winfo_x(), widget.winfo_y()
        widget.start_w = widget.winfo_width()
        widget.start_h = widget.winfo_height()


def _drag(event):
    if event.widget not in bound: return
    lst = bound[event.widget]
    for data in lst:  # 多个绑定
        if data[0] != 'drag': return
        widget = data[1]
        dx = xpos() - widget.mousex  # 计算鼠标当前位置和开始拖动时位置的差距
        # 注: 鼠标位置不能用event.x和event.y
        # event.x,event.y与控件的位置、大小有关，不能真实地反映鼠标移动的距离差值
        dy = ypos() - widget.mousey
        move(widget, widget.startx + dx if data[2] else None,
             widget.starty + dy if data[3] else None)


def _resize(event):
    data = __get(event.widget, 'resize')
    if data is None: return
    widget = data[1]
    dx = xpos() - widget.mousex  # 计算位置差
    dy = ypos() - widget.mousey

    type = data[0].lower()
    minw, minh = data[2:4]
    if 's' in type:
        move(widget, height=max(widget.start_h + dy, minh))
    elif 'n' in type:
        move(widget, y=min(widget.starty + dy, widget.starty + widget.start_h - minh),
             height=max(widget.start_h - dy, minh))

    __remove(event.widget, data[0])  # 取消绑定, 为防止widget.update()中产生新的事件, 避免_resize()被tkinter反复调用
    widget.update()  # 刷新控件, 使以下左右缩放时, winfo_height()返回的是新的控件坐标, 而不是旧的
    __add(event.widget, data)  # 重新绑定

    if 'e' in type:
        move(widget, width=max(widget.start_w + dx, minw))
    elif 'w' in type:
        move(widget, x=min(widget.startx + dx, widget.startx + widget.start_w - minw),
             width=max(widget.start_w - dx, minw))


def draggable_resizable(root, target):
    draggable(target)
    resizable(root, target)


def draggable(tkwidget, x=True, y=True):
    """调用draggable(tkwidget) 使tkwidget可拖动。
tkwidget: 一个控件(Widget)或一个窗口(Wm)。
x 和 y: 只允许改变x坐标或y坐标。"""
    tkwidget.bind('<Button-1>', adjust_buttons, add='+')
    bind_drag(tkwidget, tkwidget, x, y)


def bind_drag(tkwidget, dragger, x=True, y=True):
    """绑定拖曳事件。
tkwidget: 被拖动的控件或窗口,
dragger: 接收鼠标事件的控件,
调用bind_drag后,当鼠标拖动dragger时, tkwidget会被带着拖动, 但dragger
作为接收鼠标事件的控件, 位置不会改变。
x 和 y: 同draggable()函数。"""
    dragger.bind('<Button-1>', _mousedown, add='+')
    dragger.bind('<B1-Motion>', _drag, add='+')
    __add(dragger, ('drag', tkwidget, x, y))  # 在bound字典中记录数据


resize_buttons = []


def resizable(root, tkwidget, size=10):
    tkwidget.bind('<B1-Motion>', adjust_buttons, add='+')
    add_resize_button(root, tkwidget, lambda: (tkwidget.winfo_x() - size, tkwidget.winfo_y() - size), 'nw')
    add_resize_button(root, tkwidget, lambda: (tkwidget.winfo_x() + tkwidget.winfo_width() // 2, tkwidget.winfo_y() - size), 'n')
    add_resize_button(root, tkwidget, lambda: (tkwidget.winfo_x() + tkwidget.winfo_width(), tkwidget.winfo_y() - size), 'ne')
    add_resize_button(root, tkwidget, lambda: (tkwidget.winfo_x() + tkwidget.winfo_width(),
                      tkwidget.winfo_y() + tkwidget.winfo_height() // 2), 'e')
    add_resize_button(root, tkwidget, lambda: (tkwidget.winfo_x() + tkwidget.winfo_width(),
                      tkwidget.winfo_y() + tkwidget.winfo_height()), 'se')
    add_resize_button(root, tkwidget, lambda: (tkwidget.winfo_x() + tkwidget.winfo_width() // 2,
                      tkwidget.winfo_y() + tkwidget.winfo_height()), 's')
    add_resize_button(root, tkwidget, lambda: (tkwidget.winfo_x() - size, tkwidget.winfo_y() + tkwidget.winfo_height()), 'sw')
    add_resize_button(root, tkwidget, lambda: (tkwidget.winfo_x() - size, tkwidget.winfo_y() + tkwidget.winfo_height() // 2), 'w')


def add_resize_button(root, target, func, anchor_name, size=10):
    b = ttk.Button(root)
    b._func = func
    bind_resize(target, b, anchor_name)
    x, y = func()
    b.place(x=x, y=y, width=size, height=size)
    b.bind('<B1-Motion>', adjust_buttons, add='+')
    resize_buttons.append(b)


def adjust_buttons(event=None):
    # 改变大小或拖动后,调整手柄位置
    for b in resize_buttons:
        x, y = b._func()
        b.place(x=x, y=y)



def bind_resize(tkwidget, dragger, anchor, min_w=0, min_h=0, move_dragger=True):
    """绑定缩放事件。
anchor: 缩放"手柄"的方位, 取值为N,S,W,E,NW,NE,SW,SE,分别表示东、西、南、北。
min_w,min_h: 该方向tkwidget缩放的最小宽度(或高度)。
move_dragger: 缩放时是否移动dragger。
其他说明同bind_drag函数。"""
    dragger.bind('<Button-1>', _mousedown, add='+')
    dragger.bind('<B1-Motion>', _resize, add='+')
    data = (anchor, tkwidget, min_w, min_h, move_dragger)
    __add(dragger, data)
