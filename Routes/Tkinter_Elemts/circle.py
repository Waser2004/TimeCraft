import tkinter as tk
from math import sqrt

class Circle(object):
    def __init__(self, canvas: tk.Canvas, center: [int, int], radius: int, color: [int, int, int], outline_thickness: int,
                 outline_color: [int, int, int]):
        # assign variables
        self.canvas = canvas

        self.center = center
        self.radius = radius
        self.color = list(color)
        self.outline_thickness = outline_thickness
        self.outline_color = list(outline_color)

        # create object variable
        self.object = None

    def draw(self):
        # calculate hex color code
        fill_hex = self.__rgb_to_hex(self.color)
        outline_hex = self.__rgb_to_hex(self.outline_color) if self.outline_thickness >= 1 else None
        # draw object on the screen if it has not already been drawn
        if self.object is None:
            self.object = self.canvas.create_oval(self.center[0] - self.radius, self.center[1] - self.radius,
                                                  self.center[0] + self.radius, self.center[1] + self.radius,
                                                  fill=fill_hex, outline=outline_hex, width=self.outline_thickness)
        # update widget
        else:
            self.canvas.coords(self.object, self.center[0] - self.radius, self.center[1] - self.radius,
                               self.center[0] + self.radius, self.center[1] + self.radius)
            self.canvas.itemconfig(self.object, fill=fill_hex, outline=outline_hex, width=self.outline_thickness)

    def delete(self):
        # erase object from the screen if it has been drawn before
        if self.object is not None:
            self.canvas.delete(self.object)
            self.object = None

    # update center parameter
    def set_center(self, center: [int, int]):
        # update variable
        self.center = center
        self.draw()

    # update radius parameter
    def set_radius(self, radius: int):
        # update variable
        self.radius = radius

        if self.object is not None:
            self.draw()

    # update color parameter
    def set_color(self, color: [int, int, int]):
        # update variable
        self.color = color

        if self.object is not None:
            self.draw()

    # update outline thickness parameter
    def set_outline_thickness(self, outline_thickness: int):
        # update variable
        self.outline_thickness = outline_thickness

        if self.object is not None:
            self.draw()

    # update outline_color parameter
    def set_outline_color(self, outline_color: [int, int, int]):
        # update variable
        self.outline_color = outline_color

        if self.object is not None:
            self.draw()

    # check if it is pressed
    def is_pressed(self, x: int, y: int) -> bool:
        # is pressed
        if sqrt((x - self.center[0]) ** 2 + (y - self.center[1]) ** 2) <= self.radius:
            return True
        # is not pressed
        return False

    @staticmethod
    def __rgb_to_hex(rgb):
        return "#{:02x}{:02x}{:02x}".format(round(rgb[0]), round(rgb[1]), round(rgb[2]))
