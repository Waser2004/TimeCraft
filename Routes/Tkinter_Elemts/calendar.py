from datetime import date, datetime, time, timedelta
from math import floor
import tkinter as tk
from tkinter.font import Font
import re

from Routes.Tkinter_Elemts import entry, line, text, rectangle


class Calendar(object):
    def __init__(self, root: tk.Tk, canvas: tk.Canvas, corner_1: [int, int], corner_2: [int, int],
                 text_color: [int, int, int], secondary_color: [int, int, int], editable: bool = False):
        # Tkinter elements
        self.root = root
        self.canvas = canvas
        self.draw_state = False

        self.editable = editable

        # calendar position variables
        self.corner_1 = corner_1
        self.corner_2 = corner_2
        self.text_color = text_color
        self.secondary_color = secondary_color

        # calendar
        self.calendars = {}
        self.appointment_ids = []

        self.appointment_backgrounds = []
        self.appointment_time_labels = []
        self.appointment_name_labels = []

        # calendar settings variables
        self.viewed_days_amount = 1
        self.active_date = date.today()
        self.time_span = [time(6), time(23)]
        self.time_span = [time(6), time(23)]
        self.time_indication_delta = 1

        # pop-up
        self.pop_up_state = False
        self.pop_up_ids = None
        self.pop_up_width = 300

        self.pop_up_background = None
        self.pop_up_name_entry = None
        self.pop_up_calendar_label = None
        self.pop_up_start_label = None
        self.pop_up_start_entry = None
        self.pop_up_end_label = None
        self.pop_up_end_entry = None
        self.pop_up_location_label = None
        self.pop_up_location_entry = None
        self.pop_up_cross_p1 = None
        self.pop_up_cross_p2 = None

        # canvas element variables
        self.time_indication_lines = []
        self.time_indication_labels = []
        self.date_labels = []
        self.date_weekday_labels = []
        self.current_time_line = None

        # create canvas elements
        self.create_time_indicators()
        self.create_date_labels()
        self.create_current_time_indication_line()

        self.__update_time_indicator_loop()

    def __update_time_indicator_loop(self):
        self.create_current_time_indication_line()

        self.canvas.after(60000, self.__update_time_indicator_loop)

    # ------------------------
    # calendar setting updates
    # ------------------------
    def add_calendar(self, calendar_name, calendar):
        self.calendars.update({calendar_name: calendar})

        self.update()

    def update_calendar(self, calendar_name, appointments):
        self.calendars[calendar_name]["appointments"] = appointments

        self.update()

    def remove_calendar(self, calendar_name):
        if calendar_name in self.calendars:
            self.calendars.pop(calendar_name)

            self.update()

    def set_active_date(self, active_datetime):
        self.active_date = date(active_datetime.year, active_datetime.month, active_datetime.day)

        self.update()

    # ----------------------
    # create canvas elements
    # ----------------------
    # create time indication lines
    def create_time_indicators(self):
        # create new lines
        start_time = datetime.combine(datetime.today(), self.time_span[0])
        end_time = datetime.combine(datetime.today(), self.time_span[1])

        height_delta = self.corner_2[1] - self.corner_1[1] - 60

        # create canvas elements
        for i in range(floor((amount_of_indication_lines := (end_time - start_time).total_seconds() / 3600 / self.time_indication_delta)) + 1):
            y_pos = height_delta / amount_of_indication_lines * i + self.corner_1[1] + 50
            label_time = start_time + timedelta(hours=self.time_indication_delta * i)

            # update elements
            if i < len(self.time_indication_labels):
                self.time_indication_lines[i].set_pos([self.corner_1[0] + 30, y_pos], [self.corner_2[0], y_pos])

                self.time_indication_labels[i].set_center([self.corner_1[0], y_pos])
                self.time_indication_labels[i].set_text(label_time.strftime("%H:%M"))
            # create new elements
            else:
                self.time_indication_lines.append(line.Line(self.canvas, [self.corner_1[0] + 30, y_pos], [self.corner_2[0], y_pos], self.secondary_color, 1))
                self.time_indication_labels.append(text.Text(self.canvas, label_time.strftime("%H:%M"), [self.corner_1[0], y_pos], self.secondary_color, 10, anchor="w"))

        # delete and clear over the top indicators
        while amount_of_indication_lines + 1 < len(self.time_indication_labels):
            # delete
            self.time_indication_lines[floor(amount_of_indication_lines) + 1].delete()
            self.time_indication_labels[floor(amount_of_indication_lines) + 1].delete()

            # remove from list
            self.time_indication_lines.pop(floor(amount_of_indication_lines) + 1)
            self.time_indication_labels.pop(floor(amount_of_indication_lines) + 1)

    def create_date_labels(self):
        for day_i in range(self.viewed_days_amount):
            weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            # calculations
            row_date = date(self.active_date.year, self.active_date.month, self.active_date.day) + timedelta(days=day_i)
            x_pos = floor(self.corner_1[0] + 30 + (self.corner_2[0] - self.corner_1[0] - 30) / (self.viewed_days_amount) * (day_i + 0.5))

            # update element
            if day_i < len(self.date_labels):
                self.date_labels[day_i].set_text(row_date.strftime("%d.%m.%y"))
                self.date_labels[day_i].set_center([x_pos, self.corner_1[1]])

                self.date_weekday_labels[day_i].set_text(weekday_names[row_date.weekday()])
                self.date_weekday_labels[day_i].set_center([x_pos, self.corner_1[1] + 25])
            # create new element
            else:
                self.date_labels.append(text.Text(self.canvas, row_date.strftime("%d.%m.%y"), [x_pos, self.corner_1[1]], self.text_color, 20, anchor="n"))
                self.date_weekday_labels.append(text.Text(self.canvas, weekday_names[row_date.weekday()], [x_pos, self.corner_1[1] + 25], [color * 0.8 for color in self.text_color],10, anchor="n"))

            # delete and clear over the top indicators
            while self.viewed_days_amount < len(self.date_labels):
                self.date_labels[self.viewed_days_amount].delete()
                self.date_labels.pop(self.viewed_days_amount)

                self.date_weekday_labels[self.viewed_days_amount].delete()
                self.date_weekday_labels.pop(self.viewed_days_amount)


    @staticmethod
    def events_intersect(event_1, event_2):
        if event_1.appointment[2] > event_2.appointment[1] and event_1.appointment[1] < event_2.appointment[2]:
            return True

        return False

    def create_current_time_indication_line(self):
        # calculations
        start_time = datetime.combine(datetime.today(), self.time_span[0])
        end_time = datetime.combine(datetime.today(), self.time_span[1])

        height_delta = self.corner_2[1] - self.corner_1[1] - 60

        # convert active date into datetime
        original_datetime = datetime.combine(self.active_date, datetime.min.time())

        cur_time = (datetime.now().hour - start_time.hour) * 3600 + (datetime.now().minute - start_time.minute) * 60
        y_pos = self.corner_1[1] + 50 + (height_delta / (end_time - start_time).total_seconds()) * cur_time
        x_pos = self.corner_1[0] + 30 + (self.corner_2[0] - self.corner_1[0] - 30) / self.viewed_days_amount * floor((datetime.today() - original_datetime).total_seconds() / 86400)

        # create canvas element
        if original_datetime <= datetime.today() <= original_datetime + timedelta(days=self.viewed_days_amount) and start_time <= datetime.now() <= end_time:
            if self.current_time_line is None:
                # new element
                self.current_time_line = line.Line(self.canvas, [x_pos, y_pos], [x_pos + (self.corner_2[0] - self.corner_1[0] - 30) / self.viewed_days_amount, y_pos], self.text_color, 1)
            else:
                # update old element
                self.current_time_line.set_pos([x_pos, y_pos], [x_pos + (self.corner_2[0] - self.corner_1[0] - 30) / self.viewed_days_amount, y_pos])
                if self.draw_state:
                    self.current_time_line.draw()
        # delete line from the screen
        elif self.current_time_line is not None:
            self.current_time_line.delete()

    # -------------------------------------
    # canvas actions - draw/delete elements
    # -------------------------------------
    def draw(self):
        self.draw_state = True
        # draw time indicators
        for li, la in zip(self.time_indication_lines, self.time_indication_labels):
            li.draw()
            la.draw()

            self.canvas.tag_lower(li.object)
            self.canvas.tag_lower(la.object)

        # draw date indicators
        for la, wd_la in zip(self.date_labels, self.date_weekday_labels):
            la.draw()
            wd_la.draw()

        # draw appointments
        for bg in self.appointment_backgrounds:
            bg.draw()

        for na in self.appointment_name_labels:
            na.draw()

        for ti in self.appointment_time_labels:
            ti.draw()

            self.canvas.tag_raise(ti.object)

        # current time_line
        start_time = datetime.combine(datetime.today(), self.time_span[0])
        end_time = datetime.combine(datetime.today(), self.time_span[1])

        if self.active_date <= date.today() < self.active_date + timedelta(days=self.viewed_days_amount) and start_time <= datetime.now()  <= end_time:
            self.current_time_line.draw()
            self.canvas.tag_raise(self.current_time_line.object)

        # draw pop up
        if self.pop_up_state:
            self.draw_pop_up()

    def draw_pop_up(self):
        # draw
        self.pop_up_background.draw()
        self.pop_up_name_entry.draw()
        self.pop_up_calendar_label.draw()
        self.pop_up_start_label.draw()
        self.pop_up_start_entry.draw()
        self.pop_up_end_label.draw()
        self.pop_up_end_entry.draw()
        self.pop_up_location_label.draw()
        self.pop_up_location_entry.draw()
        self.pop_up_cross_p1.draw()
        self.pop_up_cross_p2.draw()

        # raise tags
        self.canvas.tag_raise(self.pop_up_background.object)
        self.canvas.tag_raise(self.pop_up_name_entry.text.object)
        self.canvas.tag_raise(self.pop_up_calendar_label.object)
        self.canvas.tag_raise(self.pop_up_start_label.object)
        self.canvas.tag_raise(self.pop_up_start_entry.text.object)
        self.canvas.tag_raise(self.pop_up_end_label.object)
        self.canvas.tag_raise(self.pop_up_end_entry.text.object)
        self.canvas.tag_raise(self.pop_up_location_label.object)
        self.canvas.tag_raise(self.pop_up_location_entry.text.object)
        self.canvas.tag_raise(self.pop_up_cross_p1.object)
        self.canvas.tag_raise(self.pop_up_cross_p2.object)

    def delete(self):
        self.draw_state = False
        # draw time indicators
        for li, la in zip(self.time_indication_lines, self.time_indication_labels):
            li.delete()
            la.delete()

        # draw date indicators
        for la, wd_la in zip(self.date_labels, self.date_weekday_labels):
            la.delete()
            wd_la.delete()

        # draw appointments
        for bg in self.appointment_backgrounds:
            bg.delete()
        for na in self.appointment_name_labels:
            na.delete()
        for ti in self.appointment_time_labels:
            ti.delete()

        # close pop up
        if self.pop_up_state:
            self.close_pop_up()

        # current time line
        if self.current_time_line is not None:
            self.current_time_line.delete()

    # check if time string is valid
    def check_start_time_string(self, prev_str, new_str):
        new_text = new_str if re.fullmatch(r"\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}", new_str) else prev_str

        try:
            # check if start time is before ending time
            if self.get_datetime_from_str(new_text) >= self.get_datetime_from_str(self.pop_up_end_entry.txt):
                new_text = prev_str
        except:
            new_text = prev_str

        # apply changes
        self.pop_up_start_entry.set_text(new_text)
        self.pop_up_start_entry.bind_change = lambda x: self.check_start_time_string(new_text, x)

    # check if time ending is valid
    def check_end_time_string(self, prev_str, new_str):
        new_text = new_str if re.fullmatch(r"\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}", new_str) else prev_str

        try:
            # check if start time is before ending time
            if self.get_datetime_from_str(new_text) <= self.get_datetime_from_str(self.pop_up_start_entry.txt):
                new_text = prev_str
        except:
            new_text = prev_str

        # apply changes
        self.pop_up_end_entry.set_text(new_text)
        self.pop_up_end_entry.bind_change = lambda x: self.check_end_time_string(new_text, x)

    @staticmethod
    def get_datetime_from_str(datetime_str):
        # split string into date and time
        date_str, time_str = datetime_str.split()

        # unpack strings
        day, month, year = map(int, date_str.split("."))
        hour, minute = map(int, time_str.split(":"))

        return datetime(year, month, day, hour, minute)

    # is pressed
    def is_pressed(self, event):
        if self.root.focus_get() == self.root:
            # pop_up corner 1 position
            x_pos = (self.corner_2[0] - self.corner_1[0]) / 2 + self.corner_1[0] - self.pop_up_width / 2
            y_pos = (self.corner_2[1] - self.corner_1[1]) / 2 + self.corner_1[1] - 120

            # no pop up
            if not self.pop_up_state:
                # check if an appointment ist pressed
                for i, back in enumerate(self.appointment_backgrounds):
                    if back.is_pressed(event.x, event.y):
                        # update variables
                        self.pop_up_state = True
                        self.pop_up_ids = self.appointment_ids[i]


                        # appointment parameters
                        name = self.calendars[self.appointment_ids[i][0]]["appointments"][self.appointment_ids[i][1]][0]
                        start_time = self.calendars[self.appointment_ids[i][0]]["appointments"][self.appointment_ids[i][1]][1]
                        end_time = self.calendars[self.appointment_ids[i][0]]["appointments"][self.appointment_ids[i][1]][2]
                        location = self.calendars[self.appointment_ids[i][0]]["appointments"][self.appointment_ids[i][1]][3]

                        if location is None:
                            location = ""

                        # colors
                        color = self.calendars[self.appointment_ids[i][0]]["color"]
                        outline_color = [round(color[0] * 0.8), round(color[1] * 0.8), round(color[2] * 0.8)]
                        label_color = [round(color[0] * 0.65), round(color[1] * 0.65), round(color[2] * 0.65)]


                        # create elements
                        if self.pop_up_background is None:
                            self.pop_up_background = rectangle.Rectangle(self.canvas, [floor(x_pos), floor(y_pos)], [floor(x_pos + self.pop_up_width), floor(y_pos + 240)], 10, color, 1, outline_color)
                            self.pop_up_name_entry = entry.Entry(self.root, self.canvas, name, [x_pos + 20, y_pos + 20], self.pop_up_width - 90, color, self.text_color, 20, bind=self.editable)
                            self.pop_up_calendar_label = text.Text(self.canvas, self.appointment_ids[i][0], [x_pos + 20, y_pos + 50], label_color, 10, anchor="nw")
                            self.pop_up_start_label = text.Text(self.canvas, "Starting time: ", [x_pos + 20, y_pos + 100], label_color, 15, anchor="nw")
                            self.pop_up_start_entry = entry.Entry(self.root, self.canvas, start_time.strftime('%d.%m.%Y %H:%M'), [x_pos + 140, y_pos + 100], self.pop_up_width - 160, color, self.text_color, 15, bind=self.editable)
                            self.pop_up_end_label = text.Text(self.canvas, "Ending time:", [x_pos + 20, y_pos + 135],label_color, 15, anchor="nw")
                            self.pop_up_end_entry = entry.Entry(self.root, self.canvas, end_time.strftime('%d.%m.%Y %H:%M'),[x_pos + 140, y_pos + 135], self.pop_up_width - 160, color, self.text_color, 15, bind=self.editable)
                            self.pop_up_location_label = text.Text(self.canvas, "Location:", [x_pos + 20, y_pos + 170],label_color, 15, anchor="nw")
                            self.pop_up_location_entry = entry.Entry(self.root, self.canvas, location, [x_pos + 140, y_pos + 170], self.pop_up_width - 160, color, self.text_color, 15, placeholder="No Location", bind=self.editable)
                            self.pop_up_cross_p1 = line.Line(self.canvas, [x_pos + self.pop_up_width - 40, y_pos + 20], [x_pos + self.pop_up_width - 20, y_pos + 40], label_color, 2)
                            self.pop_up_cross_p2 = line.Line(self.canvas, [x_pos + self.pop_up_width - 20, y_pos + 20], [x_pos + self.pop_up_width - 40, y_pos + 40], label_color, 2)

                            self.pop_up_start_entry.bind_change = lambda x: self.check_start_time_string(start_time.strftime('%d.%m.%Y %H:%M'), x)
                            self.pop_up_end_entry.bind_change = lambda x: self.check_end_time_string(end_time.strftime('%d.%m.%Y %H:%M'), x)
                        # update elements
                        else:
                            # update position
                            self.update_pop_up_pos()

                            # update content
                            self.pop_up_background.set_color(color)
                            self.pop_up_background.set_outline_color(outline_color)

                            self.pop_up_name_entry.set_text(name)
                            self.pop_up_name_entry.set_background_color(color)

                            self.pop_up_calendar_label.set_text(self.appointment_ids[i][0])
                            self.pop_up_calendar_label.set_color(label_color)

                            self.pop_up_start_label.set_color(label_color)

                            self.pop_up_start_entry.set_text(start_time.strftime('%d.%m.%Y %H:%M'))
                            self.pop_up_start_entry.set_background_color(color)

                            self.pop_up_end_label.set_color(label_color)

                            self.pop_up_end_entry.set_text(end_time.strftime('%d.%m.%Y %H:%M'))
                            self.pop_up_end_entry.set_background_color(color)

                            self.pop_up_location_label.set_color(label_color)

                            self.pop_up_location_entry.set_text(location)
                            self.pop_up_location_entry.set_background_color(color)

                            self.pop_up_cross_p1.set_color(label_color)
                            self.pop_up_cross_p2.set_color(label_color)

                            # update bind functions
                            self.pop_up_start_entry.bind_change = lambda x: self.check_start_time_string(start_time.strftime('%d.%m.%Y %H:%M'), x)
                            self.pop_up_end_entry.bind_change = lambda x: self.check_end_time_string(end_time.strftime('%d.%m.%Y %H:%M'), x)

                        self.draw_pop_up()

                        break
            # pop-up is active
            else:
                if not self.pop_up_background.is_pressed(event.x, event.y):
                    self.close_pop_up()

                if x_pos + self.pop_up_width - 40 <= event.x <= x_pos + self.pop_up_width - 20 and y_pos + 20 <= event.y <= y_pos + 40:
                    self.close_pop_up()

    def update_pop_up_pos(self):
        # pop_up corner 1 position
        x_pos = (self.corner_2[0] - self.corner_1[0]) / 2 + self.corner_1[0] - self.pop_up_width / 2
        y_pos = (self.corner_2[1] - self.corner_1[1]) / 2 + self.corner_1[1] - 120

        # update positions
        self.pop_up_background.set_pos([floor(x_pos), floor(y_pos)], [floor(x_pos + self.pop_up_width), floor(y_pos + 240)])
        self.pop_up_name_entry.set_corner_1([x_pos + 20, y_pos + 20])
        self.pop_up_calendar_label.set_center([x_pos + 20, y_pos + 50])
        self.pop_up_start_label.set_center([x_pos + 20, y_pos + 100])
        self.pop_up_start_entry.set_corner_1([x_pos + 140, y_pos + 100])
        self.pop_up_end_label.set_center([x_pos + 20, y_pos + 135])
        self.pop_up_end_entry.set_corner_1([x_pos + 140, y_pos + 135])
        self.pop_up_location_label.set_center([x_pos + 20, y_pos + 170])
        self.pop_up_location_entry.set_corner_1([x_pos + 140, y_pos + 170])
        self.pop_up_cross_p1.set_pos([x_pos + self.pop_up_width - 40, y_pos + 20], [x_pos + self.pop_up_width - 20, y_pos + 40])
        self.pop_up_cross_p2.set_pos([x_pos + self.pop_up_width - 20, y_pos + 20], [x_pos + self.pop_up_width - 40, y_pos + 40])

    def update(self):
        self.create_time_indicators()
        self.create_date_labels()
        self.create_calendar_appointments()
        self.create_current_time_indication_line()

        # update popup
        if self.pop_up_state:
            self.update_pop_up_pos()

        if self.draw_state:
            self.draw()

    def close_pop_up(self):
        # delete canvas elements
        self.pop_up_background.delete()
        self.pop_up_name_entry.delete()
        self.pop_up_calendar_label.delete()
        self.pop_up_start_label.delete()
        self.pop_up_start_entry.delete()
        self.pop_up_end_label.delete()
        self.pop_up_end_entry.delete()
        self.pop_up_location_label.delete()
        self.pop_up_location_entry.delete()
        self.pop_up_cross_p1.delete()
        self.pop_up_cross_p2.delete()

        # update appointment
        self.calendars[self.pop_up_ids[0]]["appointments"][self.pop_up_ids[1]] = [
            self.pop_up_name_entry.txt,
            self.get_datetime_from_str(self.pop_up_start_entry.txt),
            self.get_datetime_from_str(self.pop_up_end_entry.txt),
            self.pop_up_location_entry.txt
        ]

        # update variables
        self.pop_up_state = False
        self.pop_up_ids = None

        self.create_calendar_appointments()
        if self.draw_state:
            self.draw()

    def create_calendar_appointments(self):
        # calculations
        self.appointment_ids.clear()
        active_datetime = datetime.combine(self.active_date, datetime.min.time())
        timespan_appointment = Appointment(None, None, [
            "timespan",
            active_datetime + timedelta(hours=self.time_span[0].hour),
            active_datetime + timedelta(hours=self.time_span[1].hour) + timedelta(days=self.viewed_days_amount - 1)
        ])
        timespan = [active_datetime + timedelta(hours=self.time_span[0].hour), active_datetime + timedelta(hours=self.time_span[1].hour)]

        # create new appointment list
        appointments = []
        for calendar_i, (name, calendar) in enumerate(self.calendars.items()):
            for app_i, app in enumerate(calendar["appointments"]):
                day_timespan_appointment = Appointment(None, None, [
                    "timespan",
                    datetime.combine(app[1], self.time_span[0]),
                    datetime.combine(app[1], self.time_span[1])
                ])

                if self.events_intersect(timespan_appointment, appointment:=Appointment(name, calendar["color"], app)):
                    # split up multi day event
                    if (day_span := (appointment.appointment[2].date() - appointment.appointment[1].date()).days) > 0:
                        # set params
                        app_name = appointment.appointment[0]
                        app_loc = appointment.appointment[3]

                        # start date
                        new_appointment = Appointment(
                            name,
                            calendar["color"],
                            [app_name, appointment.appointment[1], datetime.combine(appointment.appointment[1], datetime.max.time()), app_loc]
                        )
                        # update appointment actual time params
                        new_appointment.actual_time_frame = [app[1], app[2]]

                        # append new appointment
                        if self.events_intersect(timespan_appointment, new_appointment) and self.events_intersect(day_timespan_appointment, appointment):
                            appointments.append(new_appointment)
                            self.appointment_ids.append([name, app_i])

                        # days in between
                        for day in range(day_span - 1):
                            # update datetimes
                            day_date = datetime.combine(appointment.appointment[1], datetime.min.time()) + timedelta(days=1 + day)

                            day_timespan_appointment.appointment[1] = datetime.combine(day_date, self.time_span[0])
                            day_timespan_appointment.appointment[2] = datetime.combine(day_date, self.time_span[1])

                            # create new_appointment
                            new_appointment = Appointment(
                                name,
                                calendar["color"],
                                [app_name, datetime.combine(day_date, datetime.min.time()), datetime.combine(day_date, datetime.max.time()), app_loc]
                            )
                            # update appointment actual time params
                            new_appointment.actual_time_frame = [app[1], app[2]]

                            # append new appointment
                            if self.events_intersect(timespan_appointment, new_appointment) and self.events_intersect(day_timespan_appointment, appointment):
                                appointments.append(new_appointment)
                                self.appointment_ids.append([name, app_i])

                        # update datetimes
                        day_timespan_appointment.appointment[1] = datetime.combine(appointment.appointment[2], self.time_span[0])
                        day_timespan_appointment.appointment[2] = datetime.combine(appointment.appointment[2], self.time_span[1])

                        # end datetime
                        new_appointment = Appointment(
                            name,
                            calendar["color"],
                            [app_name, datetime.combine(appointment.appointment[2], datetime.min.time()), appointment.appointment[2], app_loc]
                        )
                        # update appointment actual time params
                        new_appointment.actual_time_frame = [app[1], app[2]]

                        # append new appointment
                        if self.events_intersect(timespan_appointment, new_appointment) and self.events_intersect(day_timespan_appointment, appointment):
                            appointments.append(new_appointment)
                            self.appointment_ids.append([name, app_i])

                    # shorter than one day event
                    else:
                        if self.events_intersect(day_timespan_appointment, appointment):
                            appointments.append(appointment)
                            self.appointment_ids.append([name, app_i])

        sorted_appointments = sorted(appointments, key=lambda x: x.duration)
        sorted_appointments.reverse()

        # -----------------------------
        # creating children and parents
        # -----------------------------
        for i, app in enumerate(sorted_appointments):
            for rev_app in sorted_appointments[i + 1:]:
                # check for intersection
                if self.events_intersect(app, rev_app):
                    # only add as child if it does not intersect with another child
                    if not [self.events_intersect(child, rev_app) for child in app.children].count(True):
                        app.children.append(rev_app)
                        rev_app.parents.append(app)

        # -----------------------------
        # creating intersection lists
        # -----------------------------
        parent_appointments = []
        for app in sorted_appointments:
            # only create intersection lists on parent appointments
            if app.parents == []:
                app.intersection_lists = app.get_intersection_lists()
                parent_appointments.append(app)

        sorted_parent_appointments = sorted(parent_appointments, key=lambda x: max([len(lst) for lst in x.intersection_lists]))
        sorted_parent_appointments.reverse()

        # -----------------------------
        # set widths
        # -----------------------------
        for app in sorted_parent_appointments:
            app.set_width()

        # -----------------------------
        # create appointment elements
        # -----------------------------
        background_counter = 0
        time_label_counter = 0
        for i, app in enumerate(appointments):
            # get app height
            height = self.corner_2[1] - self.corner_1[1] - 60
            app_height = height / (timespan[1] - timespan[0]).total_seconds() * app.duration

            # get app x, y pos
            day_width = (self.corner_2[0] - (self.corner_1[0] + 30)) / self.viewed_days_amount
            day_amount = floor((app.appointment[1] - active_datetime).total_seconds() / (24 * 60 * 60))
            app_width = app.width * (day_width - 40)

            # app y start
            relative_app_start = active_datetime + timedelta(hours=app.appointment[1].hour, minutes=app.appointment[1].minute, seconds=app.appointment[1].second)
            app_y_start = (relative_app_start - timespan[0]).total_seconds() / (timespan[1] - timespan[0]).total_seconds() * height

            if relative_app_start < timespan[0]:
                app_height += app_y_start
                app_y_start = 0

            # update height if it would exceed calendar frame
            if app_height + app_y_start > height:
                app_height = height - app_y_start

            x_pos = self.corner_1[0] + 30 + 15 + day_width * day_amount + app.start * (day_width - 40) + 5
            y_pos = self.corner_1[1] + 50 + app_y_start


            # --- create canvas elements --- #
            # --- background
            # update existing one
            if i < len(self.appointment_backgrounds):
                self.appointment_backgrounds[i].set_corner_1([floor(x_pos), floor(y_pos)])
                self.appointment_backgrounds[i].set_corner_2([floor(x_pos + app_width - 10), floor(y_pos + app_height)])
                self.appointment_backgrounds[i].set_color(app.color)
            # create new one
            else:
                self.appointment_backgrounds.append(
                    rectangle.Rectangle(self.canvas, [floor(x_pos), floor(y_pos)], [floor(x_pos + app_width - 10), floor(y_pos + app_height)], 4, app.color, 0, app.color)
                )

            # --- name label --- #
            # sufficient height
            label_x_pos = x_pos + 5
            if app_height > 22:
                label_y_pos = y_pos + 5
                font_size = 12
            # height enough for full font size
            elif app_height > 12:
                label_y_pos = y_pos + floor((app_height - 12) / 2) + 1
                font_size = 12
            # not height enough for full font size
            else:
                label_y_pos = y_pos
                font_size = app_height if app_height >= 3 else 0

            # shorten name if needed
            font = Font(family="HarmonyOS Sans SC", size=-floor(font_size))
            if font.measure((name := app.appointment[0]) + "...") > app_width - 20:
                while font.measure(name+ "...") > app_width - 20:
                    # shorten name
                    name = name[:-1]

                    # break loop if name has no more characters
                    if len(name) == 0:
                        break

                name += "..."

            # update existing one
            if i < len(self.appointment_name_labels):
                self.appointment_name_labels[i].set_text(name)
                self.appointment_name_labels[i].set_center([label_x_pos, label_y_pos])
                self.appointment_name_labels[i].set_font_size(floor(font_size))
            # create new one
            else:
                self.appointment_name_labels.append(
                    text.Text(self.canvas, name, [label_x_pos, label_y_pos], self.text_color, floor(font_size), anchor="nw")
                )

            background_counter += 1

            # --- time label --- #
            # only show time if there is enough space
            if app_height > 38:
                label_color = [color * 0.65 for color in app.color]
                label_y_pos = y_pos + 22

                # set time name string
                if (app.actual_time_frame[1] - app.actual_time_frame[0]).days == 0:
                    name = f"{app.actual_time_frame[0].strftime('%H:%M')} - {app.actual_time_frame[1].strftime('%H:%M')}"
                else:
                    name = f"{app.actual_time_frame[0].strftime('%d.%m.%Y %H:%M')} - {app.actual_time_frame[1].strftime('%d.%m.%Y %H:%M')}"

                # shorten name if needed
                font = Font(family="HarmonyOS Sans SC", size=-10)
                if font.measure(name + "...") > app_width - 20:
                    while font.measure(name + "...") > app_width - 20:
                        # shorten name
                        name = name[:-1]

                        # break loop if name has no more characters
                        if len(name) == 0:
                            break

                    name += "..."

                # update existing one
                if time_label_counter < len(self.appointment_time_labels):
                    self.appointment_time_labels[time_label_counter].set_text(name)
                    self.appointment_time_labels[time_label_counter].set_center([label_x_pos, label_y_pos])
                    self.appointment_time_labels[time_label_counter].set_color(label_color)
                # create new one
                else:
                    self.appointment_time_labels.append(
                        text.Text(self.canvas, name, [label_x_pos, label_y_pos], label_color, 10, anchor="nw")
                    )

                time_label_counter += 1

        # --- delete over the top canvas elements --- #
        while background_counter < len(self.appointment_backgrounds):
            self.appointment_backgrounds[background_counter].delete()
            self.appointment_backgrounds.pop(background_counter)

            self.appointment_name_labels[background_counter].delete()
            self.appointment_name_labels.pop(background_counter)

        while time_label_counter < len(self.appointment_time_labels):
            self.appointment_time_labels[time_label_counter].delete()
            self.appointment_time_labels.pop(time_label_counter)


# Appointment class
class Appointment(object):
    def __init__(self, calendar_name, color, appointment):
        # define parameters
        self.calendar_name = calendar_name
        self.color = color
        self.appointment = appointment
        # actual time frame -> in case that a multi day appointment is split up
        self.actual_time_frame = [appointment[1], appointment[2]]

        # other parameters
        self.duration = (self.appointment[2] - self.appointment[1]).total_seconds()
        self.width = None
        self.start = None

        # parent/child Appointment
        self.parents = []
        self.children = []

        # intersection lists
        self.intersection_lists = []

    def get_intersection_lists(self):
        if not self.children:
            return [[self]]

        sequences = []
        for child in self.children:
            child_sequences = child.get_intersection_lists()
            for seq in child_sequences:
                sequences.append([self] + seq)

        return sequences

    def set_width(self):
        # children have no set width
        if [app.width for lst in self.intersection_lists for app in lst] == [None for lst in self.intersection_lists for
                                                                             _ in lst]:
            # calculate own width and set start
            self.width = 1 / max([len(lst) for lst in self.intersection_lists])
            self.start = 0

            # calculate width of children
            if len(self.children) > 0:
                for lst in self.intersection_lists:
                    width = (1 - self.width) / (len(lst) - 1)
                    for i, app in enumerate(lst[1:]):
                        app.width = width
                        app.start = self.width + width * i

        # children have set width
        else:
            widths = []
            amount_of_elms_with_no_width = []
            # loop over all intersection lists
            for lst in self.intersection_lists:
                # set params
                widths.append(1)
                amount_of_elms_with_no_width.append(0)
                # get how many appointments do not have a width and how much width is left to be occupied
                for app in lst[1:]:
                    # app with width
                    if app.width:
                        widths[-1] -= app.width
                    # app without width
                    else:
                        amount_of_elms_with_no_width[-1] += 1

            # get smallest width
            elm_widths = []
            for i, (width, amount_of_elm) in enumerate(zip(widths, amount_of_elms_with_no_width)):
                elm_widths.append([i, width / (amount_of_elm + 1)])

            # calculate own width
            sorted_elm_widths = sorted(elm_widths, key=lambda x: x[1])
            self.width = sorted_elm_widths[0][1]
            self.start = 0

            # calculate width of children
            if len(self.children) > 0:
                for i, lst in enumerate(self.intersection_lists):
                    if amount_of_elms_with_no_width[i] > 0:
                        width = (widths[i] - self.width) / (amount_of_elms_with_no_width[i])
                        for i_app, app in enumerate(lst[1:]):
                            if not app.width:
                                app.width = width
                                app.start = self.width + i_app * width

    def __repr__(self):
        return str([self.start, self.width])
