import copy
import tkinter as tk
from PIL import Image, ImageTk
import logging

# window elements
from Routes import nav_bar, home, integrations_calendar, integrations_todo_list


class GUI():
    func_logger = logging.getLogger("func_log")

    def __init__(self):
        self.win_size = [1040, 585]
        self.dispatch_message = None

        # set up window
        self.root = tk.Tk()
        self.root.geometry(f"{self.win_size[0]}x{self.win_size[1]}")
        self.root.minsize(self.win_size[0], self.win_size[1])
        ico = Image.open('Assets/TimeCraft_logo.png')
        photo = ImageTk.PhotoImage(ico)
        self.root.wm_iconphoto(False, photo)
        self.root.title("TimeCraft")

        # canvas
        self.canvas = tk.Canvas(self.root, width=self.win_size[0], height=self.win_size[1], bg="#2E3338")
        self.canvas.place(x=-2, y=-2)

        # elements
        self.nav_bar = nav_bar.Nav_Bar(self.canvas, self.win_size)

        # routes
        self.current_route = "Home"

        self.routes = {
            "Home": home.Home(self, self.canvas, self.win_size),
            "Integrations-calendar": integrations_calendar.Integrations_calendar(self, self.root, self.canvas, self.win_size),
            "Integrations-todo-list": integrations_todo_list.Integrations_Todo_List(self.root, self.canvas, self.win_size),
            "Settings-calendar-integration": None,
            "Settings-todo-list-integration": None,
            "Settings-general": None,
            "Settings-evaluation": None,
        }

        # status
        self.statuses = {
            "google calendar connection status": None,
            "google calendar statuses": None,
            "todo list statuses": None
        }

        # window event bindings
        self.root.bind_class("Tk", "<Configure>", self.resize)
        self.root.bind("<Button-1>", self.mouse_left_click)
        self.root.bind("<Button-2>", self.mouse_right_click)
        self.root.bind("<MouseWheel>", self.mouse_wheel)
        self.root.bind("<Motion>", self.mouse_movement)
        self.root.bind("<Left>", self.left_arrow)
        self.root.bind("<Right>", self.right_arrow)

        # update window protocols
        self.root.protocol("WM_DELETE_WINDOW", lambda : (self.dispatch_message(601, None)))

    # draw to the window
    def draw(self):
        self.nav_bar.draw()

        self.routes[self.current_route].draw()

    # update route
    def change_Route(self, route):
        # delete old route from screen
        self.routes[self.current_route].delete()

        # route with no redirection
        if not ["Integrations", "Settings"].count(route):
            self.current_route = route

        # redirecting
        elif route == "Integrations":
            self.current_route = "Integrations-calendar"
        elif route == "Settings":
            self.current_route = "Settings-integrations"

        # request appointments and todos if new route is Home
        if route =="Home":
            self.dispatch_message(401, None)
            self.dispatch_message(402, None)

        # draw new route
        self.routes[self.current_route].draw()

    # start window
    def mainloop(self):
        self.root.mainloop()

    # --------------------------------------
    # handle front and backend communication
    # --------------------------------------
    def set_backend_connection(self, backend_connection):
        self.dispatch_message = backend_connection

        # routes
        for _, route in self.routes.items():
            try:
                route.set_backend_connection(backend_connection)
            except:
                pass

    def receive_message(self, message_code, message):
        # log functions
        self.func_logger.info(f"[frontend] - recieve message {[message_code, message]}")

        # --- 100 -> Google Calendar Controls --- #
        # 101  => Request and send Google Calendar Status
        if message_code == 101:
            # update statuses
            self.statuses["google calendar connection status"] = message[0]
            self.statuses["google calendar status"] = message[1]

            if self.statuses["google calendar connection status"] and len(self.routes["Integrations-calendar"].google_calendar_block.calendars) == 0:
                self.dispatch_message(102, None)

            self.routes["Integrations-calendar"].set_google_calendar_status(message[0], message[1])
            # update schedule button at the start of the program
            if self.routes["Home"].init_state:
                self.routes["Home"].schedule_todos.set_color([83, 191, 102])
                self.routes["Home"].init_state = False

        # 102 => Request and send avilable google Calendar list
        elif message_code == 102:
            # update google calendar block with the calendar list
            if message is not None:
                self.routes["Integrations-calendar"].google_calendar_block.set_calendars(message)

        # 103 => Request and send Appointments
        elif message_code == 103:
            pass

        # 104 => Update google Calendars
        elif message_code == 104:
            # "AC" -> append calendar from calendars that are being taken into consideration
            if message[0] == "AC":
                pass
            # "RC" -> remove calendar from calendars that are being taken into consideration
            elif message[0] == "RC":
                pass

        # 105 => Request credential token
        if message_code == 105:
            pass

        # --- 200 -> Todo_list Controls --- #
        # 201 => Update notion integration secret
        elif message_code == 201:
            self.routes["Integrations-todo-list"].notion_secret_popup.submit_label.set_text("saved")

        # 202 => Request and send Todo_list Status
        elif message_code == 202:
            # update statuses
            self.statuses["todo list statuses"] = message

            self.routes["Integrations-todo-list"].set_notion_todo_list_statuses(message)

        # 203 => Request and send Todos
        elif message_code == 203:
            pass

        # 204 => Update Todo_lists
        elif message_code == 204:
            # "AT" -> append new todo_list to list
            if message[0] == "AT":
                self.routes["Integrations-todo-list"].add_notion_block(message[1])
                self.routes["Home"].todo_list_vis.add_todo_list(message[1], [])
            # "UT" -> Update todo_list specifications
            elif message[0] == "UT":
                self.routes["Integrations-todo-list"].notion_todo_list_blocks[message[2]] = self.routes["Integrations-todo-list"].notion_todo_list_blocks.pop(message[1])
                self.routes["Integrations-todo-list"].order = [key if key != message[1] else message[2] for key in self.routes["Integrations-todo-list"].order]

                self.routes["Integrations-todo-list"].notion_todo_list_blocks[message[2]].title_entry.set_text(message[2])
                self.routes["Integrations-todo-list"].notion_todo_list_blocks[message[2]].todo_list_name = message[2]

                self.routes["Home"].todo_list_vis.update_todo_list_name(message[1], message[2])
            # "RT" -> remove todo_list from list
            elif message[0] == "RT":
                pass

        # 205 => Update Notion tod_list hidden settings
        elif message_code == 205:
            self.routes["Home"].todo_list_vis.remove_todo_list(message[0])

        # --- 300 -> Schedule Todos --- #
        # 301 => Schedule Todos
        elif message_code == 301:
            # Update schedule todos button
            self.routes["Home"].schedule_todos.set_color([83, 191, 102])
            self.routes["Home"].schedule_todos_label.set_text("Schedule Todos")

            # add the scheduled todos to the calendar vis
            appointments = [app + [""] for app in message]
            # add new calendar
            if not "scheduled todos" in self.routes["Home"].calendar_vis.calendars:
                calendar = {"name": "scheduled todos", "color": [83, 191, 102], "appointments": appointments}
                self.routes["Home"].calendar_vis.add_calendar("scheduled todos", calendar)

            # update existing one
            else:
                self.routes["Home"].calendar_vis.update_calendar("scheduled todos", appointments)

        # --- 400 -> Home.py Requests --- #
        # 401 => Request and send Todos from/for Home.py
        elif message_code == 401:
            # update todo_list vis
            for name, todos in message.items():
                todos = copy.deepcopy(todos)
                # add new calendar
                if not name in self.routes["Home"].todo_list_vis.todo_list_blocks:
                    self.routes["Home"].todo_list_vis.add_todo_list(name, todos)

                # update existing one
                else:
                    self.routes["Home"].todo_list_vis.update_todo_list(name, todos)

                # raise tags
                if self.routes["Home"].draw_status:
                    self.canvas.tag_raise(self.routes["Home"].top_blocker.object)
                    self.canvas.tag_raise(self.routes["Home"].bottom_blocker.object)
                    self.canvas.tag_raise(self.routes["Home"].schedule_todos.object)
                    self.canvas.tag_raise(self.routes["Home"].schedule_todos_label.object)

            # delete all todo_lists that are no longer active
            to_remove_lists = []
            for key in self.routes["Home"].todo_list_vis.todo_list_blocks.keys():
                if key not in message:
                    to_remove_lists.append(key)

            for key in to_remove_lists:
                self.routes["Home"].todo_list_vis.remove_todo_list(key)

            self.routes["Home"].requesting_todos = False

        # 402 => Request and send Calendar Appointments from/for Home.py
        elif message_code == 402:
            # update calendar vis
            for name, appointments in message.items():
                # add new calendar
                if not name in self.routes["Home"].calendar_vis.calendars:
                    calendar = {
                        "name": name,
                        "color": [83, 191, 102] if name == "scheduled todos" else [56, 86, 68] if name == "done todos" else [100, 100, 100],
                        "appointments": appointments
                    }
                    self.routes["Home"].calendar_vis.add_calendar(name, calendar)

                # update existing one
                else:
                    self.routes["Home"].calendar_vis.update_calendar(name, appointments)

            self.routes["Home"].requesting_appointments = False

        # 403 => Update Todos
        elif message_code == 403:
            # "UT" -> Update todos specifications
            if message[0] == "AT":
                # remove todo_if it could not be successfully added
                if message[3][1] != 200:
                    self.routes["Home"].todo_list_vis.todo_list_blocks[message[1]].remove_todos([None])
                # update id of todo_
                else:
                    self.routes["Home"].todo_list_vis.todo_list_blocks[message[1]].todos[-1][3] = message[3][0]

            # "CT" -> set todo_state to done (check todos)
            elif message[0] == "CT":
                self.routes["Home"].todo_list_vis.todo_list_blocks[message[1]].remove_todos([message[2][3]])

        # 404 => Active Todos
        elif message_code == 404:
            self.routes["Home"].todo_list_vis.set_active_todo(message)

        # 405 => Update scheduling todos button label
        elif message_code == 405:
            self.routes["Home"].schedule_todos.set_color([100, 100, 100])
            self.routes["Home"].schedule_todos_label.set_text(message)

        # --- 600 -> close program --- #
        # 602 => end program
        elif message_code == 602:
            self.root.destroy()

    # -------------
    # window events
    # -------------
    # window resize
    def resize(self, event):
        # new window size
        self.win_size = [event.width, event.height]

        # update components size
        self.canvas.configure(width=self.win_size[0], height=self.win_size[1])
        self.nav_bar.resize(event)

        # update routes positions
        for route in self.routes.values():
            try:
                route.resize(event)
            except:
                pass

    # left click
    def mouse_left_click(self, event):
        if self.root.focus_get() == self.root:
            # navbar
            self.nav_bar.mouse_lef_click(event, self.change_Route)

            # route
            try:
                self.routes[self.current_route].mouse_left_click(event)
            except:
                pass

    # right click
    def mouse_right_click(self, event):
        if self.root.focus_get() == self.root:
            pass

    # mouse wheel
    def mouse_wheel(self, event):
        # route
        try:
            self.routes[self.current_route].mouse_wheel(event)
        except:
            pass

    # mouse movement
    def mouse_movement(self, event):
        # navbar
        self.nav_bar.mouse_movement(event)

        # route
        try:
            self.routes[self.current_route].mouse_movement(event)
        except:
            pass

    # left arrow click
    def left_arrow(self, event):
        # route
        try:
            self.routes[self.current_route].left_arrow(event)
        except:
            pass

    # right arrow click
    def right_arrow(self, event):
        # route
        try:
            self.routes[self.current_route].right_arrow(event)
        except:
            pass