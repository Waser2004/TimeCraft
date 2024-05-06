from Routes.Tkinter_Elemts import text, rectangle, calendar, todo_list
from math import ceil, floor
from datetime import date, datetime, timedelta, time
import logging

from data_loader import notion_todo_lists

class Home(object):
    func_logger = logging.getLogger("func_log")
    def __init__(self, frontend, canvas, window_size):
        self.frontend = frontend
        self.canvas = canvas
        self.win_size = window_size

        self.init_state = True

        # calendar
        self.calendar_vis = calendar.Calendar(
            self.frontend.root, self.canvas, [400, 100], [(self.win_size[0] - 300) / 2 + 250, self.win_size[1] - 160],
            [230, 230, 230], [64, 71, 79]
        )
        self.calendar_reach = [datetime.today() - timedelta(days=10), datetime.today() + timedelta(days=20)]
        self.requesting_appointments = True

        # todo_list
        self.todo_list_vis = todo_list.Todo_List(
            self.frontend.root, self.canvas, [(self.win_size[0] - 300) / 2 + 450, 100],
            [self.win_size[0] - 100, self.win_size[1] - 160], [230, 230, 230], [83, 191, 102]
        )
        self.requesting_todos = True

        self.top_blocker = rectangle.Rectangle(self.canvas, [301, 0], [self.win_size[0], 100], 0, [46, 51, 56], 0, [0, 0, 0])
        self.bottom_blocker = rectangle.Rectangle(self.canvas, [301, self.win_size[1] - 160], [self.win_size[0], self.win_size[1] + 10], 0, [46, 51, 56], 0,[0, 0, 0])

        # events to calendar button
        self.schedule_todos = rectangle.Rectangle(
            self.canvas, [(self.win_size[0] - 300) / 2 + 50, self.win_size[1] - 60],
            [(self.win_size[0] - 300) / 2 + 550, self.win_size[1] - 20], 6, [100, 100, 100],
            0, [100, 100, 100]
        )
        self.schedule_todos_label = text.Text(
            self.canvas, "Schedule Todos",
            [(self.win_size[0] - 300) / 2 + 300, self.win_size[1] - 40], [255, 255, 255], 13
        )

        # add todo_lists
        for key in notion_todo_lists.keys():
            self.todo_list_vis.add_todo_list(key, [])

        self.draw_status = False

    def draw(self):
        self.draw_status = True

        self.calendar_vis.draw()
        self.todo_list_vis.draw()

        self.top_blocker.draw()
        self.canvas.tag_raise(self.top_blocker.object)
        self.bottom_blocker.draw()
        self.canvas.tag_raise(self.bottom_blocker.object)

        self.schedule_todos.draw()
        self.canvas.tag_raise(self.schedule_todos.object)
        self.schedule_todos_label.draw()
        self.canvas.tag_raise(self.schedule_todos_label.object)

    def delete(self):
        self.draw_status = False
        # delete
        self.calendar_vis.delete()
        self.todo_list_vis.delete()

        self.top_blocker.delete()
        self.bottom_blocker.delete()

        self.schedule_todos.delete()
        self.schedule_todos_label.delete()

    def set_backend_connection(self, backend_connection):
        self.dispatch_message = backend_connection

        self.todo_list_vis.set_backend_connection(backend_connection)

    # -------------
    # window events
    # -------------
    # window resize
    def resize(self, event):
        self.win_size = [event.width, event.height]

        self.top_blocker.set_pos([301, 0], [self.win_size[0], 100])
        self.bottom_blocker.set_pos([301, self.win_size[1] - 160], [self.win_size[0], self.win_size[1] + 10])

        self.schedule_todos.set_corner_1([(self.win_size[0] - 300) / 2 + 50, self.win_size[1] - 60])
        self.schedule_todos.set_corner_2([(self.win_size[0] - 300) / 2 + 550, self.win_size[1] - 20])
        self.schedule_todos_label.set_center([(self.win_size[0] - 300) / 2 + 300, self.win_size[1] - 40])

        # --- calendar calculations --- #
        self.calendar_vis.corner_2 = [(self.win_size[0] - 300) / 2 + 250, self.win_size[1] - 160]
        self.calendar_vis.viewed_days_amount = x if (x := floor(((self.win_size[0] - 300) / 2 + - 150) / 300)) > 0  else 1
        self.calendar_vis.viewed_days_amount = x if (x := floor(((self.win_size[0] - 300) / 2 + - 150) / 300)) > 0  else 1

        start_time = datetime.combine(datetime.today(), self.calendar_vis.time_span[0])
        end_time = datetime.combine(datetime.today(), self.calendar_vis.time_span[1])

        height = self.calendar_vis.corner_2[1] - self.calendar_vis.corner_1[1]
        time_span = (end_time - start_time).total_seconds() / 1800
        self.calendar_vis.time_indication_delta = ceil(time_span / (height / 40)) / 2

        self.calendar_vis.update()

        # --- todolist --- #
        self.todo_list_vis.set_pos([(self.win_size[0] - 300) / 2 + 350, 100], [self.win_size[0] - 100, self.win_size[1] - 160])

        # raise tags
        self.canvas.tag_raise(self.top_blocker.object)
        self.canvas.tag_raise(self.bottom_blocker.object)
        self.canvas.tag_raise(self.schedule_todos.object)
        self.canvas.tag_raise(self.schedule_todos_label.object)

    # left click
    def mouse_left_click(self, event):
        # schedule Todos clicked
        if self.schedule_todos.is_pressed(event.x, event.y) and self.schedule_todos_label.text == "Schedule Todos" and \
            self.frontend.statuses["google calendar connection status"]:
            # update schedule todos button label
            self.schedule_todos_label.set_text("pleas wait, scheduling todos...")
            self.schedule_todos.set_color([100, 100, 100])

            # request backend to schedule todos
            self.dispatch_message(301, None)

        else:
            # calendar vis
            self.calendar_vis.is_pressed(event)

            # todo_list vis
            self.todo_list_vis.mouse_left_click(event)
    
    def right_arrow(self, event):
        active_datetime = datetime(
            self.calendar_vis.active_date.year,
            self.calendar_vis.active_date.month,
            self.calendar_vis.active_date.day
        )

        # update active date
        if not self.calendar_vis.pop_up_state:
            self.calendar_vis.set_active_date(active_datetime + timedelta(days=1))

            active_datetime = active_datetime + timedelta(days=1)

        # request new date range
        if (self.calendar_reach[1] - (active_datetime + timedelta(days=self.calendar_vis.viewed_days_amount))).days < 2 and not self.requesting_appointments:
            # update variables
            self.calendar_reach[1] = active_datetime + timedelta(days=8)
            self.requesting_appointments = True

            # send message
            self.dispatch_message(402, self.calendar_reach)

    def left_arrow(self, event):
        active_datetime = datetime(
            self.calendar_vis.active_date.year,
            self.calendar_vis.active_date.month,
            self.calendar_vis.active_date.day
        )

        # update active date
        if not self.calendar_vis.pop_up_state:
            self.calendar_vis.set_active_date(active_datetime - timedelta(days=1))

            active_datetime = active_datetime - timedelta(days=1)

        # request new date range
        if (active_datetime - self.calendar_reach[0]).days < 2 and not self.requesting_appointments:
            # update variables
            self.calendar_reach[0] = active_datetime - timedelta(days=8)
            self.requesting_appointments = True

            # send message
            self.dispatch_message(402, self.calendar_reach)

    # mouse wheel
    def mouse_wheel(self, event):
        self.todo_list_vis.mouse_wheel(event)

        self.calendar_vis.mouse_wheel(event)