import tkinter as tk

class Line(object):
    def __init__(self, canvas: tk.Canvas, start: [int, int], end: [int, int], color: [int, int, int], thickness: int):
        # assign variables
        self.canvas = canvas

        self.start = start
        self.end = end
        self.color = list(color)
        self.thickness = thickness

        # create object variable
        self.object = None

    def draw(self):
        # draw object on the screen if it has not already been drawn
        if self.object is None:
            self.object = self.canvas.create_line(self.start[0], self.start[1], self.end[0], self.end[1],
                                                  fill=self.__rgb_to_hex(self.color), width=self.thickness)
        # update widget
        else:
            self.canvas.coords(self.object, self.start[0], self.start[1], self.end[0], self.end[1])
            self.canvas.itemconfig(self.object, fill=self.__rgb_to_hex(self.color), width=self.thickness)

    def delete(self):
        # erase object from the screen if it has been drawn before
        if self.object is not None:
            self.canvas.delete(self.object)
            self.object = None

    # update position parameters
    def set_pos(self, start: [int, int], end: [int, int]):
        # update variables
        self.start = start
        self.end = end

        if self.object is not None:
            self.draw()

    # update start pos parameter
    def set_start_pos(self, start: [int, int]):
        # update variable
        self.start = start

        if self.object is not None:
            self.draw()

    # update end pos parameter
    def set_end_pos(self, end: [int, int]):
        # update variable
        self.end = end

        if self.object is not None:
            self.draw()

    # update color parameter
    def set_color(self, color: [int, int, int]):
        # update variable
        self.color = color

        if self.object is not None:
            self.draw()

    # update thickness parameter
    def set_thickness(self, thickness: int):
        # update variable
        self.thickness = thickness

        if self.object is not None:
            self.draw()


    @staticmethod
    def __rgb_to_hex(rgb):
        return "#{:02x}{:02x}{:02x}".format(round(rgb[0]), round(rgb[1]), round(rgb[2]))
