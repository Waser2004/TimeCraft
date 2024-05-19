import tkinter as tk
from math import floor, sqrt, sin, cos, pi

class Rectangle(object):
    def __init__(self, canvas: tk.Canvas, corner_1: [int, int], corner_2: [int, int], corner_radius: int,
                 color: [int, int, int], outline_thickness: int, outline_color: [int, int, int]):
        # assign variables
        self.canvas = canvas

        self.corner_1 = [corner_1[0] + 1, corner_1[1] + 1]
        self.corner_2 = [corner_2[0] - 1, corner_2[1] - 1]
        self.corner_radius = corner_radius
        self.color = list(color)
        self.outline_thickness = outline_thickness
        self.outline_color = list(outline_color)

        # create object variable
        self.object = None

    def __calc_outline_points(self) -> list[[int, int]]:
        points = []
        # rectangle with no corner radius
        if self.corner_radius < 1:
            points += [self.corner_1[0], self.corner_1[1], self.corner_2[0], self.corner_1[1], self.corner_2[0],
                       self.corner_2[1], self.corner_1[0], self.corner_2[1]]
        # rectangle with corner radius
        else:
            # parameters
            if abs(self.corner_1[0] - self.corner_2[0]) / 2 > self.corner_radius and abs(self.corner_1[1] - self.corner_2[1]) / 2 > self.corner_radius:
                corner_radius = self.corner_radius
            else:
                corner_radius = min(abs(self.corner_1[1] - self.corner_2[1]) / 2, abs(self.corner_1[1] - self.corner_2[1]) / 2)

            resolution = res if (res := floor((pi * corner_radius) / 2)) > 0 else 1
            # Top left corner
            center_1 = self.corner_1[0] + corner_radius, self.corner_1[1] + corner_radius
            for i in range(resolution + 1):
                angle = pi + (pi / 2) / resolution * i
                x = center_1[0] + cos(angle) * corner_radius
                y = center_1[1] + sin(angle) * corner_radius
                points.extend([x, y])

            # Top right corner
            center_2 = self.corner_2[0] - corner_radius, self.corner_1[1] + corner_radius
            for i in range(resolution + 1):
                angle = (pi / 2) - (pi / 2) / resolution * i
                x = center_2[0] + cos(angle) * corner_radius
                y = center_2[1] - sin(angle) * corner_radius
                points.extend([x, y])

            # Bottom right corner
            center_3 = self.corner_2[0] - corner_radius, self.corner_2[1] - corner_radius
            for i in range(resolution + 1):
                angle = (2 * pi) + (pi / 2) / resolution * i
                x = center_3[0] + cos(angle) * corner_radius
                y = center_3[1] + sin(angle) * corner_radius
                points.extend([x, y])

            # Bottom left corner
            center_4 = self.corner_1[0] + corner_radius, self.corner_2[1] - corner_radius
            for i in range(resolution + 1):
                angle = (pi / 2) - (pi / 2) / resolution * i
                x = center_4[0] - cos(angle) * corner_radius
                y = center_4[1] + sin(angle) * corner_radius
                points.extend([x, y])

        return points

    def draw(self):
        # calculate outline points
        points = self.__calc_outline_points()
        fill_hex = self.__rgb_to_hex(self.color)
        outline_hex = self.__rgb_to_hex(self.outline_color)

        # draw object on the screen if it has not already been drawn
        if self.object is None:
            self.object = self.canvas.create_polygon(
                points,
                fill=fill_hex,
                outline=outline_hex if self.outline_thickness > 0 else fill_hex,
                width=self.outline_thickness if self.outline_thickness > 0 else 1
            )

        # update widget
        else:
            self.canvas.coords(self.object, points)
            self.canvas.itemconfig(
                self.object,
                fill=fill_hex,
                outline=outline_hex if self.outline_thickness > 0 else fill_hex,
                width=self.outline_thickness + 1 if self.outline_thickness > 0 else 1
            )

    def delete(self):
        # erase object from the screen if it has been drawn before
        if self.object is not None:
            self.canvas.delete(self.object)
            self.object = None

    # update rect position
    def set_pos(self, corner_1: [int, int], corner_2: [int, int]):
        # update variables
        self.set_corner_1(corner_1)
        self.set_corner_2(corner_2)

    # update corner 1 parameter
    def set_corner_1(self, corner_1: [int, int]):
        # update variables
        self.corner_1 = [corner_1[0] + 1, corner_1[1] + 1]

        if self.object is not None:
            self.draw()

    # update corner 2 parameter
    def set_corner_2(self, corner_2: [int, int]):
        # update variables
        self.corner_2 = [corner_2[0] - 1, corner_2[1] - 1]

        if self.object is not None:
            self.draw()

    # update corner radius parameter
    def set_corner_radius(self, corner_radius: int):
        # update variables
        self.corner_radius = corner_radius

        if self.object is not None:
            self.draw()

    # update color parameter
    def set_color(self, color: [int, int, int]):
        # update variables
        self.color = color

        if self.object is not None:
            self.draw()

    # update outline thickness parameter
    def set_outline_thickness(self, outline_thickness: int):
        # update variables
        self.outline_thickness = outline_thickness

        if self.object is not None:
            self.draw()

    # update outline_color parameter
    def set_outline_color(self, outline_color: [int, int, int]):
        # update variables
        self.outline_color = outline_color

        if self.object is not None:
            self.draw()

    # check if it is pressed
    def is_pressed(self, x: int, y: int) -> bool:
        corner_1 = [self.corner_1[0] - 1, self.corner_1[1] - 1]
        corner_2 = [self.corner_2[0] + 1, self.corner_2[1] + 1]

        # is probably pressed
        if corner_1[0] <= x <= corner_2[0] and corner_1[1] <= y <= corner_2[1]:
            # no corner radius
            if self.corner_radius <= 1:
                return True
            # left side
            elif corner_1[0] <= x <= corner_1[0] + self.corner_radius:
                # click in top left corner
                if corner_1[1] <= y <= corner_1[1] + self.corner_radius:
                    center = [corner_1[0] + self.corner_radius, corner_1[1] + self.corner_radius]
                    if sqrt((x - center[0]) ** 2 + (y - center[1]) ** 2) <= self.corner_radius:
                        return True
                    return False
                # click in bottom left corner
                elif corner_2[1] - self.corner_radius <= y <= corner_2[1]:
                    center = [corner_1[0] + self.corner_radius, corner_2[1] - self.corner_radius]
                    if sqrt((x - center[0]) ** 2 + (y - center[1]) ** 2) <= self.corner_radius:
                        return True
                    return False
                # click between top and bottom left corner
                else:
                    return True
            # right side
            elif corner_2[0] <= x <= corner_2[0] + self.corner_radius:
                # click in top right corner
                if corner_1[1] <= y <= corner_1[1] + self.corner_radius:
                    center = [corner_1[0] + self.corner_radius, corner_2[1] - self.corner_radius]
                    if sqrt((x - center[0]) ** 2 + (y - center[1]) ** 2) <= self.corner_radius:
                        return True
                    return False
                # click in bottom right corner
                elif corner_2[1] - self.corner_radius <= y <= corner_2[1]:
                    center = [corner_2[0] - self.corner_radius, corner_2[1] - self.corner_radius]
                    if sqrt((x - center[0]) ** 2 + (y - center[1]) ** 2) <= self.corner_radius:
                        return True
                    return False
                # click between top and bottom right corner
                else:
                    return True
            # rest of the rectangle
            else:
                return True
        # is not pressed
        return False

    @staticmethod
    def __rgb_to_hex(rgb):
        return "#{:02x}{:02x}{:02x}".format(round(rgb[0]), round(rgb[1]), round(rgb[2]))
