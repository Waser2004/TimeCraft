import tkinter as tk
from tkinter.font import Font

class Text(object):
    def __init__(self, canvas: tk.Canvas, text: str, center: [int, int], color: [int, int, int], font_size: int = 15,
                 font_family: str = "HarmonyOS Sans SC", anchor=tk.CENTER):
        # assign variables
        self.canvas = canvas

        self.text = text
        self.center = center
        self.color = list(color)
        self.font_size = font_size
        self.font_family = font_family
        self.anchor = anchor

        self.font = Font(family=self.font_family, size=-self.font_size)

        # create object variable
        self.object = None

    def draw(self):
        if self.font_size != 0:
            # draw object on the screen if it has not already been drawn
            if self.object is None:
                self.object = self.canvas.create_text(self.center[0], self.center[1], text=self.text, font=self.font, fill=self.__rgb_to_hex(self.color), anchor=self.anchor)
            # update widget
            else:
                self.canvas.coords(self.object, self.center[0], self.center[1])
                self.canvas.itemconfig(self.object, text=self.text, font=self.font, fill=self.__rgb_to_hex(self.color), anchor=self.anchor)

    def delete(self):
        # erase object from the screen if it has been drawn before
        if self.object is not None:
            self.canvas.delete(self.object)
            self.object = None

    # update text parameter
    def set_text(self, text: str):
        # update variable
        self.text = text

        # draw on screen
        if self.object is not None and self.font_size != 0:
            self.draw()

    # update center parameter
    def set_center(self, center: [int, int]):
        # update variable
        self.center = center
        if self.object is not None and self.font_size != 0:
            self.draw()

    # update color parameter
    def set_color(self, color: [int, int, int]):
        # update variable
        self.color = color
        if self.object is not None and self.font_size != 0:
            self.draw()

    # update font_size parameter
    def set_font_size(self, font_size: int):
        # update variable
        self.font_size = font_size
        self.font.configure(size=-self.font_size)

        # draw
        if self.object is not None and self.font_size != 0:
            self.draw()
        # font size is zero do not draw
        else:
            self.delete()

    # update font_family parameter
    def set_font_family(self, font_family: str):
        # update variable
        self.font_family = font_family
        self.font.configure(family=self.font_family)
        if self.object is not None and self.font_size != 0:
            self.draw()

    # update anchor parameter
    def set_anchor(self, anchor):
        # update variable
        self.anchor = anchor
        if self.object is not None and self.font_size != 0:
            self.draw()

    @staticmethod
    def __rgb_to_hex(rgb):
        return "#{:02x}{:02x}{:02x}".format(round(rgb[0]), round(rgb[1]), round(rgb[2]))
