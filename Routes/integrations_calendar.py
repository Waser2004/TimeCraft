from Routes.Tkinter_Elemts import checkbox, line, image, text, rectangle
from tkinter import NW
from datetime import datetime
import logging
import os
import json

from data_loader import google_calendars

class Integrations_calendar(object):
    func_logger = logging.getLogger("func_log")

    def __init__(self, frontend, root, canvas, window_size):
        self.frontend = frontend
        self.root = root
        self.canvas = canvas
        self.win_size = window_size

        self.draw_state = False

        # scrolling variable
        self.y_scroll = 0

        # create google Calendar block
        self.google_calendar_height = 125
        self.google_calendar_block = Google_Calendar_Block(self.frontend, self.canvas, self.win_size, self.set_google_calendar_height)

        # notion secret button
        self.google_login_background = rectangle.Rectangle(
            self.canvas,
            [self.win_size[0] - 50, self.win_size[1] - 50],
            [self.win_size[0] - 10, self.win_size[1] - 10],
            6,
            [37, 41, 45],
            0,
            [41, 46, 50]
        )
        self.google_login_img = image.Tk_Image(self.canvas, [self.win_size[0] - 29, self.win_size[1] - 29], "Assets/Google_logo.png", anchor="center")

    # update y pos
    def update_y_pos(self):
        # update google calendar y pos
        self.google_calendar_block.set_y_scroll(- self.y_scroll)

    # set google calendar y
    def set_google_calendar_height(self, height):
        # set height
        self.google_calendar_height = height

        # update y pos
        self.update_y_pos()

    def set_google_calendar_status(self, connection_status, statuses):
        self.google_calendar_block.set_statuses(connection_status, statuses)

    # -------------------------
    # drawing/erasing functions
    # -------------------------
    def draw(self):
        self.draw_state = True

        # google calendar block
        self.google_calendar_block.draw()

        # draw button
        self.google_login_background.draw()
        self.google_login_img.draw()

    def delete(self):
        self.draw_state = False

        # google calendar block
        self.google_calendar_block.delete()

        # delete button
        self.google_login_background.delete()
        self.google_login_img.delete()

    # --------------------------------------
    # handle front and backend communication
    # --------------------------------------
    def set_backend_connection(self, backend_connection):
        # self
        self.dispatch_message = backend_connection

        # google calendar block
        self.google_calendar_block.set_backend_connection(backend_connection)

    # -------------
    # window events
    # -------------
    # window resize
    def resize(self, event):
        # set win size
        self.win_size = [event.width, event.height]

        # update y pos
        self.update_y_pos()

        # update button
        self.google_login_background.set_pos([self.win_size[0] - 50, self.win_size[1] - 50], [self.win_size[0] - 10, self.win_size[1] - 10])
        self.google_login_img.set_center([self.win_size[0] - 29, self.win_size[1] - 29])

        # google calendar block
        self.google_calendar_block.resize(event)

    # left click
    def mouse_left_click(self, event):
        # google calendar block
        self.google_calendar_block.mouse_left_click(event)

        # request token button pressed
        if self.google_login_background.is_pressed(event.x, event.y):
            self.dispatch_message(105, None)

    # right click
    def mouse_right_click(self, event):
        # google calendar block
        self.google_calendar_block.mouse_left_click(event)

    def mouse_wheel(self, event):
        # scroll
        if self.google_calendar_height > self.win_size[1]:
            # scroll up
            if self.y_scroll + 10 <= self.google_calendar_height - self.win_size[1] and event.delta < 0:
                self.y_scroll += 10
            # set to max scroll
            elif event.delta < 0:
                self.y_scroll = self.google_calendar_height - self.win_size[1]

            # scroll down
            elif self.y_scroll - 10 >= 0 and event.delta > 0:
                self.y_scroll -= 10
            # set to min scroll
            elif event.delta > 0:
                self.y_scroll = 0

            self.update_y_pos()


########################################################################################################################
# google Calendar block
########################################################################################################################
class Google_Calendar_Block(object):
    active_at_start = google_calendars
    def __init__(self, frontend, canvas, window_size, set_height):
        self.frontend = frontend
        self.win_size = window_size
        self.canvas = canvas
        self.set_height = set_height

        self.calendar_colors = [[103, 146, 137], [244, 192, 149], [58, 80, 107], [238, 46, 49], [247, 154, 211],
                                [249, 194, 46], [90, 83, 83], [132, 147, 36]]

        # calendar list
        self.calendars = {}

        # y_scroll
        self.y_scroll = 0

        left_x = (self.win_size[0] - 300) / 2
        self.title = text.Text(self.canvas, "Google Calendars", [left_x, 50], [230, 230, 230], 20, anchor=NW)
        self.vertical_line = line.Line(self.canvas, [left_x + 15, 85], [left_x + 15, 100], [64, 71, 79], 1)

        # calender labels
        self.calendar_labels = []
        self.calendar_checkboxes = []
        self.indicator_lines = []

        # error indications
        self.connection_status = None
        self.statuses = []
        self.status_indicator_img = None

        # draw status if true things are drawn if false things ar not drawn
        self.draw_status = False

    def set_y_scroll(self, y):
        # update y scroll
        self.y_scroll = y

        # update positions
        self.update_positions()

    def update_positions(self):
        left_x = (self.win_size[0] - 300) / 2
        # update title
        self.title.set_center([left_x, self.y_scroll + 50])
        self.vertical_line.set_pos([left_x + 10, self.y_scroll + 85], [left_x + 10, self.y_scroll + 68 + len(self.calendars) * 31 if len(self.calendar_labels) > 0 else 100])

        # update calender options
        for i, (label, checkbox, line) in enumerate(zip(self.calendar_labels, self.calendar_checkboxes, self.indicator_lines)):
            label.set_center([left_x + 60, self.y_scroll + 90 + i * 31])
            checkbox.set_corner_1([left_x + 37, self.y_scroll + 93 + i * 31])
            checkbox.set_corner_2([left_x + 47, self.y_scroll + 103 + i * 31])
            line.set_pos([left_x + 10, self.y_scroll + 98 + i * 31], [left_x + 22, self.y_scroll + 98 + i * 31])

        # error indicators
        if self.status_indicator_img is not None and not self.connection_status:
            self.status_indicator_img.set_center([left_x - 40, self.y_scroll + 75])
        elif self.status_indicator_img is not None:
            self.status_indicator_img.set_center([left_x - 40, self.y_scroll + 25 + (73 + len(self.calendars) * 31) / 2])

    def set_calendars(self, calendars):
        if calendars is not None:
            # delete existing labels
            for name, check, connector in zip(self.calendar_labels, self.calendar_checkboxes, self.indicator_lines):
                name.delete()
                check.delete()
                connector.delete()

            # clear lists
            self.calendar_labels.clear()
            self.calendar_checkboxes.clear()
            self.indicator_lines.clear()

            self.calendars = calendars

            left_x = (self.win_size[0] - 300) / 2
            # create labels and checkboxes for calendars
            for i, (key, value) in enumerate(self.calendars.items()):
                # label
                self.calendar_labels.append(
                    text.Text(self.canvas, key, [left_x + 60, self.y_scroll + 90 + i * 31], [230, 230, 230], 15, anchor=NW)
                )
                # checkbox
                self.calendar_checkboxes.append(
                    checkbox.Checkbox(self.canvas, [left_x + 37, self.y_scroll + 93 + i * 31], [left_x + 47, self.y_scroll + 103 + i * 31], 0, self.calendar_colors[i], 1, [230, 230, 230])
                )
                # line
                self.indicator_lines.append(
                    line.Line(self.canvas, [left_x + 10, self.y_scroll + 98 + i * 31], [left_x + 22, self.y_scroll + 98 + i * 31],[64, 71, 79], 1)
                )

                # activate checkbox if calendar is active at start
                if key in self.active_at_start:
                    self.calendar_checkboxes[-1].state = True

                # draw label/checkbox if self is visible
                if self.draw_status:
                    self.calendar_labels[-1].draw()
                    self.calendar_checkboxes[-1].draw()
                    self.indicator_lines[-1].draw()

            # update vertical/spacer line position
            self.vertical_line.set_end_pos([left_x + 10, self.y_scroll + 68 + len(self.calendars) * 31])

            # error indicators
            if self.status_indicator_img is not None and not self.connection_status:
                self.status_indicator_img.set_center([left_x - 40, self.y_scroll + 75])
            elif self.status_indicator_img is not None:
                self.status_indicator_img.set_center([left_x - 40, self.y_scroll + 25 + (73 + len(self.calendars) * 31) / 2])

            # update height for other calendars
            self.set_height(100 + len(self.calendars) * 31)

    def set_statuses(self, connection_status, statuses):
        self.connection_status = connection_status

        # indicate connection error
        if not self.connection_status:
            self.status_indicator_img = image.Tk_Image(self.canvas, [(self.win_size[0] - 300) / 2 - 40, self.y_scroll + 75], "Assets/error_red.png")
        # indicate appointment retrival error
        elif False in statuses:
            self.status_indicator_img = image.Tk_Image(self.canvas, [(self.win_size[0] - 300) / 2 - 40, self.y_scroll + 25 + (73 + len(self.calendars) * 31) / 2], "Assets/error_yellow.png")
        # no error
        elif self.status_indicator_img is not None:
            self.status_indicator_img.delete()
            self.status_indicator_img = None

        # draw image if required
        if self.draw_status and self.status_indicator_img is not None:
            self.status_indicator_img.draw()


    # --------------------------------------
    # handle front and backend communication
    # --------------------------------------
    def set_backend_connection(self, backend_connection):
        self.dispatch_message = backend_connection
    
    # -------------------------
    # drawing/erasing functions
    # -------------------------
    def draw(self):
        self.title.draw()
        self.vertical_line.draw()

        # draw calendar options
        for label, checkbox, line in zip(self.calendar_labels, self.calendar_checkboxes, self.indicator_lines):
            label.draw()
            checkbox.draw()
            line.draw()

        # error indicators
        if self.status_indicator_img is not None:
            self.status_indicator_img.draw()

        self.draw_status = True

    def delete(self):
        self.title.delete()
        self.vertical_line.delete()

        # draw calendar options
        for label, checkbox, line in zip(self.calendar_labels, self.calendar_checkboxes, self.indicator_lines):
            label.delete()
            checkbox.delete()
            line.delete()

        # error indicators
        if self.status_indicator_img is not None:
            self.status_indicator_img.delete()

        self.draw_status = False

    # -------------
    # window events
    # -------------
    # window resize
    def resize(self, event):
        self.win_size = [event.width, event.height]

        # update positions
        self.update_positions()

    # left click
    def mouse_left_click(self, event):
        for i, cb in enumerate(self.calendar_checkboxes):
            # check if checkbox is pressed
            if cb.is_pressed(event.x, event.y):
                # add calendar to calendar list in the backend
                if cb.state:
                    message = {self.calendar_labels[i].text: self.calendars[self.calendar_labels[i].text]}
                    self.dispatch_message(104, ["AC", message])
                # remove calendar to calendar list in the backend
                else:
                    message = {self.calendar_labels[i].text: self.calendars[self.calendar_labels[i].text]}
                    self.frontend.routes["Home"].calendar_vis.remove_calendar(self.calendar_labels[i].text)

                    self.dispatch_message(104, ["RC", message])

                # break loop
                break

    # right click
    def mouse_right_click(self, event):
        pass
