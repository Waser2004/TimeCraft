from .Tkinter_Elemts import line, rectangle, text
from tkinter import W
import logging

class Nav_Bar(object):
    func_logger = logging.getLogger("func_log")

    def __init__(self, canvas, window_size):
        self.canvas = canvas
        self.win_size = window_size

        # Navigation options
        self.options = {
            "Home": [],
            "Integrations": ["calendar", "todo-list"],
            "Settings": ["calendar integration", "todo-list integration", "general", "evaluation"]
        }

        # Navbar option labels and Separators
        self.option_labels = []
        self.separators = []

        self.bounding_boxes = {}

        # Background
        self.background = rectangle.Rectangle(canvas, [-10, 0], [300, self.win_size[1] + 3],
                                              15, [28, 31, 34], 1, [28, 31, 34])

    def draw(self):
        self.background.draw()

        # loop over each navigation option
        y = 1
        for key, val in self.options.items():
            # create main navigation option
            self.option_labels.append(
                text.Text(self.canvas, key, [25, y + 25], [255, 255, 255], 20, anchor=W)
            )
            self.option_labels[-1].draw()

            # add bounding box
            box_size = [y, y + 50]
            self.bounding_boxes.update({f"{key}" : box_size})

            # increase y
            y += 50

            # check if there are sub options
            if len(val) > 0:
                # loop over sub options
                for i, label in enumerate(val):
                    # create sub options
                    self.option_labels.append(
                        text.Text(self.canvas, label, [40, y + 20], [230, 230, 230], 17, anchor=W)
                    )
                    self.option_labels[-1].draw()

                    # add bounding box
                    self.bounding_boxes.update({f"{key}-{label}": [y, y + 40 if i < len(val) - 1 else y + 43]})

                    # increase y
                    y += 40 if i < len(val) - 1 else 43

            # create seperator
            self.separators.append(
                line.Line(self.canvas, [25, y], [275, y], [40, 45, 50], 1)
            )
            self.separators[-1].draw()

    def resize(self, event):
        # update window size
        self.win_size = [event.width, event.height]

        # resize background
        self.background.set_corner_2([300, self.win_size[1] + 2])

    def mouse_lef_click(self, event, func):
        # check if navbar is clicked on
        if self.background.is_pressed(event.x, event.y):
            # iterate over bounding boxes to check if one of them was pressed
            for key, value in self.bounding_boxes.items():
                if value[0] <= event.y <= value[1]:
                    # change to clicked route
                    func(key)

                    # log function
                    self.func_logger.info(f"[nav_bar] - new active page is {key}")

                    break
    def mouse_movement(self, event):
        pass