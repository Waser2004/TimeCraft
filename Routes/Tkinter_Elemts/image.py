import tkinter as tk
from PIL import Image, ImageTk

class Tk_Image(object):
    def __init__(self, canvas: tk.Canvas, center: [int, int], src: str = None, anchor: str = "nw"):
        self.canvas = canvas
        self.pos = center
        self.src = src
        self.anchor = anchor

        self.object = None

        self.img = ImageTk.PhotoImage(Image.open(self.src))

        self.foreground = False
        self.background = False

    # draw image
    def draw(self):
        # draw if it hasn't been drawn jet
        if self.object is None and self.src is not None:
            self.object = self.canvas.create_image((self.pos[0], self.pos[1]), image=self.img, anchor=self.anchor)

    # erase image
    def delete(self):
        if self.object is not None:
            self.canvas.delete(self.object)
            self.object = None

    # change position
    def set_center(self, center: [int, int]):
        # set class parameters
        self.pos = center

        # change position
        if self.object is not None:
            self.canvas.coords(self.object, self.pos[0], self.pos[1])
            self.canvas.tag_raise(self.object, tk.ALL)

    # change image
    def set_img(self, path: str):
        self.src = path
        self.img = ImageTk.PhotoImage(Image.open(self.src))

        # update image
        if self.object is not None:
            self.canvas.itemconfigure(self.object, image=self.img)

    # check if it is pressed
    def is_pressed(self, event):
        if self.pos[0] <= event.x <= self.pos[0] + self.img.width() and self.pos[1] <= event.y <= self.pos[1] + self.img.height():
            return True

        return False