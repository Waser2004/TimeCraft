import tkinter as tk

from Routes.Tkinter_Elemts import rectangle, line

class Checkbox(object):
    def __init__(self, canvas: tk.Canvas, corner_1: [int, int], corner_2: [int, int], corner_radius: int,
                 color: [int, int, int], outline_thickness: int, outline_color: [int, int, int]):
        self.canvas = canvas

        # checkmark state True = checked / False = unchecked
        self.state = False
        
        # position variables
        self.corner_1 = corner_1
        self.corner_2 = corner_2
        self.corner_radius = corner_radius
        
        # color arguments
        self.color = color
        self.outline_color = outline_color
        
        # outline thickness
        self.outline_thickness = outline_thickness
        
        # checkmark
        inner_rect_corner_1 = [corner_1[0] + outline_thickness + 1, corner_1[1] + outline_thickness + 1]
        inner_rect_corner_2 = [corner_2[0] - outline_thickness - 1, corner_2[1] - outline_thickness - 1]
        self.inner_rect = rectangle.Rectangle(self.canvas, inner_rect_corner_1, inner_rect_corner_2, corner_radius,
                                              color, 0, [0, 0, 0])
        
        # checkmark outline
        self.outer_lines = [
            line.Line(self.canvas, corner_1, [corner_1[0], corner_2[1]], outline_color, outline_thickness),
            line.Line(self.canvas, [corner_1[0], corner_2[1]], corner_2, outline_color, outline_thickness),
            line.Line(self.canvas, corner_2, [corner_2[0], corner_1[1]], outline_color, outline_thickness),
            line.Line(self.canvas, [corner_2[0], corner_1[1]], corner_1, outline_color, outline_thickness)
        ]

    def draw(self):
        # draw checkmark
        if self.state:
            self.inner_rect.draw()
        
        # draw outline
        for line in self.outer_lines:
            line.draw()

    def delete(self):
        # delete checkmark
        self.inner_rect.delete()

        # delete outline
        for line in self.outer_lines:
            line.delete()

    # update rect position
    def set_pos(self, corner_1: [int, int], corner_2: [int, int]):
        # update variables
        self.set_corner_1(corner_1)
        self.set_corner_2(corner_2)

    # update corner 1 parameter
    def set_corner_1(self, corner_1: [int, int]):
        # update variables
        self.corner_1 = corner_1

        # update checkmark
        self.inner_rect.set_corner_1([self.corner_1[0] + self.outline_thickness + 1, self.corner_1[1] + self.outline_thickness + 1])

        # update outline
        self.outer_lines[0].set_pos(self.corner_1, [self.corner_1[0], self.corner_2[1]])
        self.outer_lines[1].set_pos([self.corner_1[0], self.corner_2[1]], self.corner_2)
        self.outer_lines[2].set_pos(self.corner_2, [self.corner_2[0], self.corner_1[1]])
        self.outer_lines[3].set_pos([self.corner_2[0], self.corner_1[1]], self.corner_1)

    # update corner 2 parameter
    def set_corner_2(self, corner_2: [int, int]):
        # update variables
        self.corner_2 = corner_2

        # update checkmark
        self.inner_rect.set_corner_2([self.corner_2[0] - self.outline_thickness - 1, self.corner_2[1] - self.outline_thickness - 1])

        # update outline
        self.outer_lines[0].set_pos(self.corner_1, [self.corner_1[0], self.corner_2[1]])
        self.outer_lines[1].set_pos([self.corner_1[0], self.corner_2[1]], self.corner_2)
        self.outer_lines[2].set_pos(self.corner_2, [self.corner_2[0], self.corner_1[1]])
        self.outer_lines[3].set_pos([self.corner_2[0], self.corner_1[1]], self.corner_1)

    # update corner radius parameter
    def set_corner_radius(self, corner_radius: int):
        # update variables
        self.corner_radius = corner_radius

        # update checkmark
        self.inner_rect.set_corner_radius(self.corner_radius)

    # update color parameter
    def set_color(self, color: [int, int, int]):
        # update variables
        self.color = color

        # update checkmark
        self.inner_rect.set_color(self.corner_radius)

    # update outline thickness parameter
    def set_outline_thickness(self, outline_thickness: int):
        # update variables
        self.outline_thickness = outline_thickness

        # update outline
        self.outer_lines[0].set_thickness(self.outline_thickness)
        self.outer_lines[1].set_thickness(self.outline_thickness)
        self.outer_lines[2].set_thickness(self.outline_thickness)
        self.outer_lines[3].set_thickness(self.outline_thickness)

    # update outline_color parameter
    def set_outline_color(self, outline_color: [int, int, int]):
        # update variables
        self.outline_color = outline_color

        # update outline
        self.outer_lines[0].set_color(self.outline_color)
        self.outer_lines[1].set_color(self.outline_color)
        self.outer_lines[2].set_color(self.outline_color)
        self.outer_lines[3].set_color(self.outline_color)

    # set status
    def set_status(self, status):
        # uncheck
        if not status:
            self.inner_rect.delete()
            self.state = False
        # check
        else:
            self.inner_rect.draw()
            self.state = True

    # check if it is pressed
    def is_pressed(self, x: int, y: int) -> bool:
        # ius pressed
        if self.corner_1[0] <= x <= self.corner_2[0] and self.corner_1[1] <= y <= self.corner_2[1]:
            # uncheck
            if self.state:
                self.inner_rect.delete()
                self.state = False
            # check
            else:
                self.inner_rect.draw()
                self.state = True

            return True
        
        return False