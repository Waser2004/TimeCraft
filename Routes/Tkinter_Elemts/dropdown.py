import copy
import tkinter as tk
from math import floor
from Routes.Tkinter_Elemts import rectangle, text

class Dropdown(object):
    def __init__(self, canvas: tk.Canvas, options: list[str], default_option: int, corner_1: [int, int],
                 width: int, corner_radius: int, background_color: [int, int, int], font_color: [int, int, int],
                 outline_color: [int, int, int], outline: int):
        # screen
        self.canvas = canvas

        # dropdown options
        self.options = copy.copy(options)
        self.current_option = default_option

        # position arguments
        self.corner_1 = corner_1
        self.width = width
        self.corner_radius = corner_radius

        # colors
        self.background_color = background_color
        self.font_color = font_color
        self.outline_color = outline_color
        self.outline = outline

        # dropdown elements
        self.draw_state = False
        self.drop_down_state = False
        self.background = rectangle.Rectangle(self.canvas, self.corner_1, [self.corner_1[0] + self.width, self.corner_1[1] + 35], self.corner_radius, self.background_color, self.outline, self.outline_color)
        self.label = text.Text(self.canvas, self.options[self.current_option], [self.corner_1[0] + 10, self.corner_1[1] + 10], self.font_color, 15, anchor="nw")

        self.dd_background = rectangle.Rectangle(self.canvas, [self.corner_1[0], self.corner_1[1] + 45], [self.corner_1[0] + self.width, self.corner_1[1] + 10 + 35 * (1 + len(self.options))], self.corner_radius, self.background_color, self.outline, self.outline_color)
        self.option_labels = [text.Text(self.canvas, txt,[self.corner_1[0] + 10, self.corner_1[1] + 55 + i * 35], self.font_color, 15, anchor="nw") for i, txt in enumerate(self.options)]

    def set_dropdown_state(self, state):
        self.drop_down_state = state

        # delete drop down
        if not self.drop_down_state:
            self.dd_background.delete()
            for label in self.option_labels:
                label.delete()

        self.update()

    # ---------------------------
    # draw/delete/update elements
    # ---------------------------
    def draw(self):
        self.draw_state = True

        # drop down base
        self.background.draw()
        self.label.draw()

        # drop down
        if self.drop_down_state:
            self.dd_background.draw()
            for label in self.option_labels:
                label.draw()

    def delete(self):
        self.draw_state = False

        # drop down base
        self.background.delete()
        self.label.delete()

        # drop down
        self.dd_background.delete()
        for label in self.option_labels:
            label.delete()

    def update(self):
        # drop down base
        self.background.set_pos(self.corner_1, [self.corner_1[0] + self.width, self.corner_1[1] + 35])

        self.label.set_center([self.corner_1[0] + 10, self.corner_1[1] + 10])
        self.label.set_text(self.options[self.current_option])

        # drop down
        self.dd_background.set_pos([self.corner_1[0], self.corner_1[1] + 45], [self.corner_1[0] + self.width, self.corner_1[1] + 10 + 35 * (1 + len(self.options))])
        for i, label in enumerate(self.option_labels):
            label.set_center([self.corner_1[0] + 10, self.corner_1[1] + 55 + i * 35])

        if self.draw_state:
            self.draw()

    # ---------------------------
    # window events
    # ---------------------------
    def mouse_left_click(self, event):
        # update drop down state
        if self.background.is_pressed(event.x, event.y):
            self.set_dropdown_state(False if self.drop_down_state else True)

        # manage press on dropdown
        elif self.dd_background.is_pressed(event.x, event.y):
            self.current_option = floor((event.y - self.corner_1[1] - 45) / 35)

            self.set_dropdown_state(False)

        # close dropdown if nothing is pressed
        elif self.drop_down_state:
            self.set_dropdown_state(False)
