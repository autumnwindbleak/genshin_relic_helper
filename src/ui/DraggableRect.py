from tkinter import *

from src.ui.UITools import draggable_resizable

class DraggableRect:
    rect = None

    def __init__(self, root, x, y, width, height):
        self.root = root
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def create(self):
        rect = Canvas(self.root, width=self.width, height=self.height, bg="white", highlightthickness=10, highlightbackground="black")
        rect.place(x=self.x, y=self.y, width=self.width, height=self.height)
        self.root.update()
        draggable_resizable(self.root, rect)
        # self.root.mainloop()
        self.root.update()
        self.rect = rect
        return rect

