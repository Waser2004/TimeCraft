import json
import threading
import copy
import logging
import time
import webbrowser
from datetime import datetime, timedelta

from Integrations.google_calendar_integration import Google_Calendar_Integration
from Integrations.notion_todo_list_integration import Notion_Todo_List_Integration
from genetic import Genetic_Algorithm

from data_loader import todos_calendar, done_todos_calendar

class Backend(object):
    # create loggers
    thread_logger = logging.getLogger("thread_log")
    func_logger = logging.getLogger("func_log")

    def __init__(self, google_calendars, notion_todo_lists, notion_todo_lists_hidden, notion_integration_secret):
        # frontend connections
        self.dispatch_message = None

        # data
        self.todos = {}
        self.retrieved_calendars = {}

        # genetic algorithm
        self.genetic_algorithm = Genetic_Algorithm({}, [])
        self.todo_calendar = []
        self.todo_order = []
        self.locked_todos = []
        self.todo_calendar_locks = []
        self.done_todo_calendar = []

        # calendar names and todolist notion ids
        self.google_calendar_connection_status = None
        self.google_calendar_statuses = []
        self.google_calendars = google_calendars

        # statuses
        self.notion_integration_secret = notion_integration_secret
        self.todo_list_status = []
        self.notion_todo_lists = notion_todo_lists
        self.notion_todo_lists_hidden = notion_todo_lists_hidden

        # Calendar/Todolist integrations
        self.update_counter = 0
        self.calendar_span = None
        self.todo_lists = {}

        # list of Google calendars
        self.calendar_list = None

        # threads
        self.running = True
        self.threads = {}
        self.loop_thread = []

        self.backend_loop()

        # logging threads
        self.thread_logger.info(f"started:    [backend loop] - currently {threading.active_count()} threads open")

    # ----
    # loop
    # ----
    def backend_loop(self):
        # --- thread management --- #
        # join old timer loop
        if len(self.loop_thread) > 1:
            self.loop_thread[0].join()
            self.loop_thread.pop(0)

        terminations = []
        # join finished threads
        try:
            for key, thread in self.threads.items():
                # join thread
                if not thread.is_alive():
                    # logging threads
                    self.thread_logger.info(f"terminated: [{key}] - currently {threading.active_count()} threads open")

                    thread.join()
                    terminations.append(key)

                    # handle successful google login
                    if key == "request token":
                        self.google_calendar_connection_status = True

                        # send messages
                        self.dispatch_message(101, [self.google_calendar_connection_status, self.google_calendar_statuses])

                        # get calendar list
                        if not "get calendar list" in self.threads:
                            # get calendar list
                            thread = threading.Thread(target=lambda: (self.get_calendar_list(), self.dispatch_message(102, self.calendar_list)), daemon=True)
                            thread.start()

                            # add thread to threads dict
                            self.threads.update({"get calendar list": thread})

                            # logging threads
                            self.thread_logger.info(f"started:    [get calendar list] - currently {threading.active_count()} threads open")

                        # send homepy appointments
                        if not "send_homepy_appointments" in self.threads:
                            # request to send appointments
                            thread = threading.Thread(target=lambda: self.send_homepy_appointments(self.calendar_span), daemon=True)

                            thread.start()
                            self.threads.update({"send_homepy_appointments": thread})

                            # logging threads
                            self.thread_logger.info(f"started:    [send_homepy_appointments] - currently {threading.active_count()} threads open")

        # handle error when new thread is being added to threads dict while looping over it
        except RuntimeError:
            pass

        # pop terminated threads from threads list.
        for name in terminations:
            self.threads.pop(name)

        # --- update todo_lists and calendars --- #
        if self.update_counter >= 60:
            if not "send_homepy_todos" in self.threads:
                # request to send appointments
                thread = threading.Thread(target=self.send_homepy_todos, daemon=True)
                thread.start()

                # add thread to threads dict
                self.threads.update({"send_homepy_todos": thread})

                # logging threads
                self.thread_logger.info(f"started:    [send_homepy_todos] - currently {threading.active_count()} threads open")

                # send homepy appointments
                if not "send_homepy_appointments" in self.threads:
                    # request to send appointments
                    thread = threading.Thread(target=lambda: self.send_homepy_appointments(self.calendar_span), daemon=True)

                    thread.start()
                    self.threads.update({"send_homepy_appointments": thread})

                    # logging threads
                    self.thread_logger.info(f"started:    [send_homepy_appointments] - currently {threading.active_count()} threads open")

            self.update_counter = 0
        # update counter
        else:
            self.update_counter += 1

        # end everything if config saved
        if "save config" in terminations:
            # request to send appointments
            thread = threading.Thread(target=lambda: self.dispatch_message(602, None), daemon=True)

            thread.start()
            self.threads.update({"terminate frontend": thread})

            # logging threads
            self.thread_logger.info(f"started:    [terminate frontend] - currently {threading.active_count()} threads open")

        # --- keep backend loop running --- #
        self.loop_thread.append(threading.Timer(1, self.backend_loop))
        self.loop_thread[-1].start()

    # ---------------
    # backend actions
    # ---------------
    def get_appointments(self, time_span):
        # log function
        self.func_logger.info("[backend] - get appointments")

        # get appointments
        appointments = {}

        self.google_calendar_statuses.clear()

        # get google calendar appointments
        for calendar, key in self.google_calendars.items():
            # successfully got appointments
            try:
                while True:
                    # execute function if the integration is ot requesting anything right now
                    if not self.google_calendar_integration.requesting:
                        appointments.update({calendar: copy.deepcopy(self.google_calendar_integration.get_appointments(key, time_span))})
                        break
                    # wait for the integration to be done requesting
                    else:
                        time.sleep(0.3)

                self.google_calendar_statuses.append(True)
            # error while trying to get appointments
            except:
                self.google_calendar_statuses.append(False)

        # update statuses
        self.dispatch_message(101, [self.google_calendar_connection_status, self.google_calendar_statuses])

        # set calendars
        self.retrieved_calendars = copy.deepcopy(appointments)

        return appointments

    def get_todos(self):
        # log function
        self.func_logger.info("[backend] - get todos")

        while True:
            # try getting todos and look aut for RunTime errors caused by dictionary changes while looping
            try:
                # get todos
                todos = {}
                self.todo_list_status.clear()
                for (name, todo_list), hidden in zip(self.todo_lists.items(), self.notion_todo_lists_hidden.values()):
                    if not hidden:
                        # successfully got todos
                        try:
                            while True:
                                # execute function if the integration is ot requesting anything right now
                                if not todo_list.requesting:
                                    todos.update({name: todo_list.get_open_tasks()})
                                    break
                                # wait for the integration to be done requesting
                                else:
                                    time.sleep(0.3)

                            self.todo_list_status.append(True)
                        # error while trying to get todos
                        except:
                            self.todo_list_status.append(False)

                    else:
                        self.todo_list_status.append(True)

                break
            # wait half a second if dictionary size has been changed and continue on then
            except RuntimeError:
                time.sleep(0.5)

        # remove hidden todos if in the meantime the hidden values have changed
        for key, value in self.notion_todo_lists_hidden.items():
            if value and key in todos:
                todos.pop(key)

        # check state of active todo_
        for key, todo in self.todos.items():
            if todo["todo states"]["active"] and todo["properties"]["status"] != "Done":
                if self.todo_lists[todo["todo list"]].get_todo_status(key) == "Done":
                    todo = [todo["properties"]["name"], None, None, "Done", key]

                    # create thread to for updating schedule
                    thread = threading.Thread(target=lambda : self.update_schedule_calendar_for_done_todo(todo), daemon=True)
                    thread.start()

                    self.threads.update({f"schedule todos for done todo {todo[0]}": thread})

                    # logging threads
                    self.thread_logger.info(f"started:    [schedule todos for done todo {todo[0]}] - currently {threading.active_count()} threads open")

                    break

        # update statuses
        self.dispatch_message(202, self.todo_list_status)

        # update todos variable
        for todo_list_key, todo_list in todos.items():
            for todo in todo_list:
                if not todo[4] in self.todos:
                    # add new todo_to todos variable
                    self.todos.update({
                        todo[4]: {
                            "todo list": todo_list_key,
                            "properties": {
                                "name": todo[0],
                                "estimated time": todo[1],
                                "extra time": 0,
                                "elapsed duration": 0,
                                "priority": todo[2],
                                "status": todo[3]
                            },
                            "todo states": {
                                "active": False,
                                "locked": False,
                                "hidden": False,
                            },
                            "order index": None,
                            "appointments": None
                        }
                    })
                # update properties
                else:
                    self.todos[todo[4]]["properties"].update({
                        "name": todo[0],
                        "estimated time": todo[1],
                        "priority": todo[2],
                        "status": todo[3]
                    })

        # send todos to home.py
        self.dispatch_message(401, todos)

        return todos

    def retime_todos(self, start_time):
        # clean todos
        self.genetic_algorithm.set_tasks(self.todos)
        todos = sorted(copy.deepcopy(self.genetic_algorithm.todos), key=lambda x: x[1]["order index"])
        locked_todos = copy.deepcopy(self.genetic_algorithm.locked_todos)

        # clean up appointments
        appointments = []
        for _, calendar in self.retrieved_calendars.items():
            appointments += calendar

        appointments = sorted(appointments, key=lambda x: x[1])

        # get timed tasks
        return self.genetic_algorithm.calculate_task_times(locked_todos + todos, appointments, start_time)


    def move_scheduled_todo_up(self, todo_id):
        # bring todos into the right order
        ordered_todos = sorted([[key, todo] for key, todo in self.todos.items() if todo["order index"] is not None], key=lambda x: x[1]["order index"])

        # rearrange order indexes only if index is not 0
        if (index := self.todos[todo_id]["order index"]) > 0:

            if index == 1:
                # update active todo_
                self.set_active_todo([self.todos[todo_id]["todo list"], todo_id])

                # split up prev todo_appointment when more than five minutes have passed
                now = datetime.now().replace(second=0, microsecond=0)
                if (prev_dur := (now - self.todos[ordered_todos[0][0]]["appointments"][-1][0]).total_seconds()) >= 300:
                    self.todos[ordered_todos[0][0]]["appointments"][-1][1] = now
                    self.todos[ordered_todos[0][0]]["appointments"].append([now, now])

                    self.todos[ordered_todos[0][0]]["properties"]["elapsed duration"] += prev_dur / 3600

            # update order indexes
            self.todos[ordered_todos[index][0]]["order index"] -= 1
            self.todos[ordered_todos[index - 1][0]]["order index"] += 1

            # lock todos
            for i, todo in enumerate(ordered_todos):
                if not ordered_todos[i + 1][0] == todo_id:
                    self.todos[todo[0]]["todo states"]["locked"] = True

                else:
                    self.todos[todo_id]["todo states"]["locked"] = True
                    break

            # calculate timed tasks
            timed_todos = self.retime_todos(datetime.now() if index == 1 else ordered_todos[0][1]["appointments"][-1][0])

            # assign appointments to todos
            for i, app in enumerate(timed_todos):
                self.todos[app[0]]["order index"] = i

                # todo_with now appointments
                if self.todos[app[0]]["appointments"] is None:
                    self.todos[app[0]]["appointments"] = [[app[1].replace(second=0, microsecond=0), app[2].replace(second=0, microsecond=0)]]

                # todo_with existing appointment
                else:
                    self.todos[app[0]]["appointments"][-1] = [app[1].replace(second=0, microsecond=0), app[2].replace(second=0, microsecond=0)]

            # merge appointments if possible
            if len(self.todos[todo_id]["appointments"]) > 1:
                app_1 = self.todos[todo_id]["appointments"][-2]
                app_2 =self.todos[todo_id]["appointments"][-1]

                # merge if time between two appointments is lower than 5min
                if 0 <= (time_between := (app_2[0] - app_1[1]).total_seconds()) <= 300:
                    # remove duration of first todo_appointment form elapsed time list
                    self.todos[todo_id]["properties"]["elapsed duration"] -= (app_1[1] - app_1[0]).total_seconds() / 3600

                    # merge todos
                    self.todos[todo_id]["appointments"][-2][1] = app_2[1]
                    self.todos[todo_id]["appointments"].pop(-1)
                    self.todos[todo_id]["properties"]["extra time"] += time_between / 3600

            # send new scheduled todo_calendar to frontend
            self.dispatch_message(402, {"scheduled todos": self.get_todo_calendar()})

    def move_scheduled_todo_down(self, todo_id):
        # bring todos into the right order
        ordered_todos = sorted([[key, todo] for key, todo in self.todos.items() if todo["order index"] is not None], key=lambda x: x[1]["order index"])

        # rearrange order indexes only if todo_is not last in list
        if (index := self.todos[todo_id]["order index"]) < len(ordered_todos) - 1:

            # split appointment if prev duration was more than 5min
            if index == 0:
                # update active todo_
                self.set_active_todo([self.todos[ordered_todos[index + 1][0]]["todo list"], ordered_todos[index + 1][0]])

                # split up prev todo_appointment when more than five minutes have passed
                now = datetime.now().replace(second=0, microsecond=0)
                if (prev_dur := (now - self.todos[todo_id]["appointments"][-1][0]).total_seconds()) >= 300:
                    self.todos[todo_id]["appointments"][-1][1] = now
                    self.todos[todo_id]["appointments"].append([now, now])

                    self.todos[todo_id]["properties"]["elapsed duration"] += prev_dur / 3600

            # update order indexes
            self.todos[ordered_todos[index][0]]["order index"] += 1
            self.todos[ordered_todos[index + 1][0]]["order index"] -= 1

            # lock todos
            for i, todo in enumerate(ordered_todos):
                self.todos[todo[0]]["todo states"]["locked"] = True

                if ordered_todos[i][0] == todo_id:
                    self.todos[ordered_todos[i + 1][0]]["todo states"]["locked"] = True
                    break

            # calculate timed tasks
            timed_todos = self.retime_todos(datetime.now() if index == 0 else ordered_todos[0][1]["appointments"][-1][0])

            # assign appointments to todos
            for i, app in enumerate(timed_todos):
                self.todos[app[0]]["order index"] = i

                # todo_with now appointments
                if self.todos[app[0]]["appointments"] is None:
                    self.todos[app[0]]["appointments"] = [[app[1].replace(second=0, microsecond=0), app[2].replace(second=0, microsecond=0)]]

                # todo_with existing appointment
                else:
                    self.todos[app[0]]["appointments"][-1] = [app[1].replace(second=0, microsecond=0), app[2].replace(second=0, microsecond=0)]

            # merge appointments if possible
            if len(self.todos[ordered_todos[index + 1][0]]["appointments"]) > 1:
                ref_todo_id = ordered_todos[index + 1][0]
                app_1 = self.todos[ref_todo_id]["appointments"][-2]
                app_2 = self.todos[ref_todo_id]["appointments"][-1]

                # merge if time between two appointments is lower than 5min
                if 0 <= (time_between := (app_2[0] - app_1[1]).total_seconds()) <= 300:
                    # remove duration of first todo_appointment form elapsed time list
                    self.todos[ref_todo_id]["properties"]["elapsed duration"] -= (app_1[1] - app_1[0]).total_seconds() / 3600

                    # merge todos
                    self.todos[ref_todo_id]["appointments"][-2][1] = app_2[1]
                    self.todos[ref_todo_id]["appointments"].pop(-1)
                    self.todos[ref_todo_id]["properties"]["extra time"] += time_between / 3600

            # send new scheduled todo_calendar to frontend
            self.dispatch_message(402, {"scheduled todos": self.get_todo_calendar()})

    def lock_todo(self, todo_id):
        # bring todos into the right order
        ordered_todos = sorted([[key, todo] for key, todo in self.todos.items() if todo["order index"] is not None], key = lambda x: x[1]["order index"])

        # unlock todo_
        if self.todos[todo_id]["todo states"]["locked"]:
            for todo in reversed(ordered_todos):
                # unlock todos that come before locked todo_
                self.todos[todo[0]]["todo states"]["locked"] = False

                if todo[0] == todo_id:
                    break

        # lock todo_
        else:
            # get index of the todo_
            for todo in ordered_todos:
                # lock todos that come before locked todo_
                self.todos[todo[0]]["todo states"]["locked"] = True

                if todo[0] == todo_id:
                    break

        # calculate timed tasks
        timed_todos = self.retime_todos(ordered_todos[0][1]["appointments"][-1][0])

        # assign appointments to todos
        for i, app in enumerate(timed_todos):
            self.todos[app[0]]["order index"] = i

            # todo_with now appointments
            if self.todos[app[0]]["appointments"] is None:
                self.todos[app[0]]["appointments"] = [[app[1].replace(second=0, microsecond=0), app[2].replace(second=0, microsecond=0)]]

            # todo_with existing appointment
            else:
                self.todos[app[0]]["appointments"][-1] = [app[1].replace(second=0, microsecond=0), app[2].replace(second=0, microsecond=0)]

        # send new scheduled todo_calendar to frontend
        self.dispatch_message(402, {"scheduled todos": self.get_todo_calendar()})

    def get_todo_calendar(self):
        todo_calendar = []
        todo_locks = []

        # create appointments and lock list
        for key, todo in self.todos.items():
            if todo["properties"]["status"] != "Done" and todo["appointments"] is not None:
                todo_calendar += [[todo["properties"]["name"]] + app + [""] + [key] for app in todo["appointments"]]
                todo_locks += [todo["todo states"]["locked"] for _ in todo["appointments"]]

        return todo_calendar, todo_locks

    def get_locked_task_ids(self):
        clean_calendar = []
        for app in self.todo_calendar:
            if clean_calendar.count(app[4]) == 0:
                clean_calendar.append(app[4])

        return [todo_id for i, todo_id in enumerate(clean_calendar) if self.locked_todos[i]]

    def schedule_todos(self, start_time = None):
        # log function
        self.func_logger.info(f"[backend] - schedule todos -> {start_time}")

        # update Schedule todo_button
        self.dispatch_message(405, "getting todo and calendar data...")

        # ############################### #
        # get calendar and todo_list data #
        # ############################### #
        # get appointments
        calendars = self.get_appointments([datetime.combine(datetime.today(), datetime.min.time()), datetime.today() + timedelta(days=5)])

        # clean up appointments
        appointments = []
        for _, calendar in calendars.items():
            appointments += calendar

        # get todos
        self.get_todos()
        ref_todos = [0 for todo in self.todos.values() if not todo["todo states"]["hidden"]]

        # ############## #
        # schedule todos #
        # ############## #
        if len(ref_todos) > 0:
            # add appointments and todos to evaluation class
            self.genetic_algorithm.set_appointments(appointments)
            self.genetic_algorithm.set_tasks(self.todos)

            # update Schedule todo_button
            self.dispatch_message(405, "evaluating best todo order...")

            # evaluate
            timed_todos = self.genetic_algorithm.evaluate(start_time)

            # add appointments to todos
            for i, app in enumerate(timed_todos):
                self.todos[app[0]]["order index"] = i

                # todo_with now appointments
                if self.todos[app[0]]["appointments"] is None:
                    self.todos[app[0]]["appointments"] = [[app[1].replace(second=0, microsecond=0), app[2].replace(second=0, microsecond=0)]]

                # todo_with existing appointment
                else:
                    self.todos[app[0]]["appointments"][-1] = [app[1].replace(second=0, microsecond=0), app[2].replace(second=0, microsecond=0)]

            # create todo_calendar
            self.todo_calendar = self.get_todo_calendar()[0]

            # create todos list sorted by order index
            todos = sorted([[key, todo] for key, todo in self.todos.items()], key=lambda x: (x[1]["order index"] is None, x[1]["order index"]))

            # ########################################################################## #
            # create thread to reschedule events at the end of the first appointment end #
            # ########################################################################## #
            if "time till scheduled event ends" in self.threads:
                self.threads["time till scheduled event ends"].cancel()
                self.threads.pop("time till scheduled event ends")

                # logging threads
                self.thread_logger.info(f"canceled:   [time till scheduled event ends] -> due to scheduling events - currently {threading.active_count()} threads open")

            # create thread that executes before appointment ist done
            thread = threading.Timer((todos[0][1]["appointments"][-1][1] - datetime.now()).total_seconds(), self.update_schedule_calendar_at_event_end)
            thread.start()

            self.threads.update({"time till scheduled event ends": thread})

            # logging threads
            self.thread_logger.info(f"started:    [time till scheduled event ends] - currently {threading.active_count()} threads open")

            # ################ #
            # set active todo_ #
            # ################ #
            ids = [todos[0][1]["todo list"], todos[0][0]]

            # only set todo_to active if it is starting or has started already
            if todos[0][1]["appointments"][0][0] <= datetime.now().replace(second=0, microsecond=0):
                self.set_active_todo(ids)

            # set time for active todo_
            else:
                # create timer
                thread = threading.Timer((todos[0][1]["appointments"][0][0] - datetime.now()).total_seconds(), lambda: self.set_active_todo(ids))
                thread.start()

                self.threads.update({"set active todo": thread})

                # logging threads
                self.thread_logger.info(f"started:    [set active todo] - currently {threading.active_count()} threads open")

        # send message that todos are scheduled
        self.dispatch_message(402, {"done todos": [self.done_todo_calendar, None]})
        self.dispatch_message(301, self.get_todo_calendar())

    def set_active_todo(self, ids):
        # send message
        self.dispatch_message(404, ids)

        # set prev active todo_to inactive
        for todo in self.todos.values():
            if todo["todo states"]["active"]:
                todo["todo states"]["active"] = False
                break

        # update todo_
        self.todos[ids[1]]["todo states"]["active"] = True
        self.todos[ids[1]]["todo states"]["locked"] = True

    def send_homepy_todos(self):
        # log function
        self.func_logger.info("[backend] - send home.py todos")

        self.get_todos()

    def send_homepy_appointments(self, time_span):
        # log function
        self.func_logger.info(f"[backend] - send home.py appointments -> timespan: {time_span}")

        self.calendar_span = time_span
        self.dispatch_message(402, {key: [value, None] for key, value in self.get_appointments(self.calendar_span).items()})

    def update_schedule_calendar_at_event_end(self):
        # log function
        self.func_logger.info("[backend] - update schedule calendar at event end")

        # get active todo_
        active_todo = None
        for key, todo in self.todos.items():
            if todo["todo states"]["active"]:
                active_todo = key
                break

        # get appointments
        calendars = self.get_appointments([datetime.combine(datetime.today(), datetime.min.time()), datetime.combine(datetime.today(), datetime.max.time())])

        appointments = []
        for _, calendar in calendars.items():
            appointments += calendar

        # sort appointments
        now = datetime.now()
        sorted(appointments, key=lambda appointment: appointment[1])
        appointments = [app for app in appointments if app[2] > now]

        # get duration to next appointment
        if len(appointments) > 0:
            time_to_next_app = (appointments[0][1] - self.todos[active_todo]["appointments"][-1][1]).total_seconds()
        else:
            time_to_next_app = 301

        # give extra time for todo_
        self.todos[active_todo]["properties"]["extra time"] += 5 / 60

        # add new todo_appointment if extension would intersect with the next calendar appointment
        if not time_to_next_app / 60 >= 5:
            # extend todo_appointment and add elapsed time
            self.todos[active_todo]["appointments"][-1][1] += timedelta(seconds=time_to_next_app)
            self.todos[active_todo]["properties"]["elapsed duration"] += (self.todos[active_todo]["appointments"][-1][1] - self.todos[active_todo]["appointments"][-1][0]).total_seconds() / 3600

            # add appointment
            self.todos[active_todo]["appointments"].append([appointments[0][2], appointments[0][2] + timedelta(seconds=300 - time_to_next_app)])

        # schedule todos
        self.genetic_algorithm.todos.clear()
        self.schedule_todos()

    def update_schedule_calendar_for_done_todo(self, todo):
        pause_time = 1

        # log function
        self.func_logger.info(f"[backend] - update schedule calendar for done todo -> {todo}")

        # remove done todo_from list
        self.todo_lists[self.todos[todo[4]]["todo list"]].set_task_status_to_done(todo)
        self.todos[todo[4]]["properties"]["status"] = "Done"
        self.todos[todo[4]]["order index"] = None

        # send frontend that todo_is set done
        self.dispatch_message(403, ["CT", self.todos[todo[4]]["todo list"], todo])

        schedule_start = datetime.now()

        # check if todo_was active
        if self.todos[todo[4]]["todo states"]["active"]:
            # update todo_appointments
            if self.todos[todo[4]]["appointments"][-1][0] < (now := datetime.now().replace(second=0, microsecond=0)):
                self.todos[todo[4]]["appointments"][-1][1] = now

            # last todo_appointment has not started jet
            else:
                self.todos[todo[4]]["appointments"].pop(-1)

            # move todo_appointments to done todo_calendar
            name = self.todos[todo[4]]["properties"]["name"]
            self.done_todo_calendar += [[name] + app + [""] + [todo[4]] for app in self.todos[todo[4]]["appointments"]]

            # send set no todo_to be active
            self.dispatch_message(404, None)

            # cancel update schedule calendar at event end thread
            if "time till scheduled event ends" in self.threads:
                self.threads["time till scheduled event ends"].cancel()

                # logging threads
                self.thread_logger.info(f"canceled:   [time till scheduled event ends] -> due to done todo - currently {threading.active_count()} threads open")

            # update schedule start
            schedule_start += timedelta(minutes=pause_time)

        # schedule todos
        self.genetic_algorithm.todos.clear()
        self.schedule_todos(schedule_start)

    # --------------------------------------
    # handle front and backend communication
    # --------------------------------------
    def set_frontend_connection(self, frontend_connection):
        # log function
        self.func_logger.info("[backend] - set frontend connection")

        self.dispatch_message = frontend_connection

    def clear_calendars(self):
        for key in self.google_calendars.keys():
            self.dispatch_message(104, ["RC", key])

        self.google_calendars.clear()

    def receive_message(self, message_code, message):
        # log function
        self.func_logger.info(f"[backend] - retrieve message {[message_code, message]}")

        # --- 100 -> Google Calendar Controls --- #
        # 101  => Request and send Google Calendar Status
        if message_code == 101:
            self.dispatch_message(101, [self.google_calendar_connection_status, self.google_calendar_statuses])

        # 102 => Request and send avilable google Calendar list
        elif message_code == 102:
            if not "get calendar list" in self.threads:
                # get calendar list
                thread = threading.Thread(target=lambda: (self.get_calendar_list(), self.dispatch_message(102, self.calendar_list)), daemon=True)
                thread.start()

                # add thread to threads dict
                self.threads.update({"get calendar list": thread})

                # logging threads
                self.thread_logger.info(f"started:    [get calendar list] - currently {threading.active_count()} threads open")

        # 103 => Request and send Appointments
        elif message_code == 103:
            pass

        # 104 => Update google Calendars
        elif message_code == 104:
            # "AC" -> append calendar from calendars that are being taken into consideration
            if message[0] == "AC":
                self.google_calendars.update(message[1])

                # send homepy appointments
                if not "send_homepy_appointments" in self.threads:
                    # request to send appointments
                    thread = threading.Thread(target=lambda: self.send_homepy_appointments(self.calendar_span), daemon=True)
                    thread.start()
                    self.threads.update({"send_homepy_appointments": thread})

                    # logging threads
                    self.thread_logger.info(f"started:    [send_homepy_appointments] - currently {threading.active_count()} threads open")

            # "RC" -> remove calendar from calendars that are being taken into consideration
            elif message[0] == "RC":
                self.google_calendars.pop(list(message[1].keys())[0])

        # 105 => Request credential token
        elif message_code == 105:
            if not self.google_calendar_integration.requesting_token:
                # request token via thread
                thread = threading.Thread(target=lambda: (self.google_calendar_integration.request_token(), self.clear_calendars()), daemon=True)
                thread.start()

                self.threads.update({"request token": thread})

                # logging threads
                self.thread_logger.info(f"started:    [send_homepy_appointments] - currently {threading.active_count()} threads open")
            else:
                webbrowser.open(self.google_calendar_integration.flow.authorization_url(prompt='consent')[0])

        # --- 200 -> Todo_list Controls --- #
        # 201 => Update notion integration secret
        elif message_code == 201:
            # update parameters
            self.notion_integration_secret = message

            for value in self.todo_lists.values():
                value.update_notion_integration_secret(message)

            # update todo_information on the home page
            if not "send_homepy_todos" in self.threads:
                # request to send appointments
                thread = threading.Thread(target=self.send_homepy_todos, daemon=True)
                thread.start()

                # add thread to threads dict
                self.threads.update({"send_homepy_todos": thread})

                # logging threads
                self.thread_logger.info(f"started:    [send_homepy_todos] - currently {threading.active_count()} threads open")

            # return message
            self.dispatch_message(201, message)

        # 202 => Request and send Todo_list Status
        elif message_code == 202:
            self.dispatch_message(202, self.todo_list_status)

        # 203 => Request and send Todos
        elif message_code == 203:
            pass

        # 204 => Update Todo_lists
        elif message_code == 204:
            # "AT" -> append new todo_list to list
            if message[0] == "AT":
                # todo_list name already given
                if message[1] in self.todo_lists:
                    # create new name
                    i = 1
                    while True:
                        # name is already given
                        if f"{message[1]} {i}" in self.todo_lists:
                            i += 1
                        # set new calendar name
                        else:
                            message[1] = f"{message[1]} {i}"
                            break

                # add todolist
                self.todo_lists.update({message[1]: Notion_Todo_List_Integration(message[1], self.notion_integration_secret)})
                self.notion_todo_lists_hidden.update({message[1]: False})

                # dispatch message with name
                self.dispatch_message(204, ["AT", message[1]])

            # "UT" -> Update todo_list specifications
            elif message[0] == "UT":
                # todo_list name already given
                if message[1] != message[2][0] and message[2][0] in self.todo_lists:
                    # create new name
                    i = 1
                    while True:
                        # name is already given
                        if f"{message[2][0]} {i}" in self.todo_lists:
                            i += 1
                        # set new todo_list name
                        else:
                            message[2][0] = f"{message[2][0]} {i}"
                            break

                # update todolist name
                if message[1] != message[2][0]:
                    # dispatch message with new name
                    self.dispatch_message(204, ["UT", message[1], message[2][0]])

                    # --- update dicts --- #
                    new_todo_list_dict = {}
                    new_hidden_dict = {}
                    for key, value in self.todo_lists.items():
                        # keep old values
                        if key != message[1]:
                            new_todo_list_dict.update({key: value})
                            new_hidden_dict.update({key: self.notion_todo_lists_hidden[key]})
                        # set changed values
                        else:
                            new_todo_list_dict.update({message[2][0]: value})
                            new_hidden_dict.update({message[2][0]: self.notion_todo_lists_hidden[key]})

                    # override
                    self.todo_lists = copy.copy(new_todo_list_dict)
                    self.notion_todo_lists_hidden = copy.copy(new_hidden_dict)

                # change key
                self.todo_lists[message[2][0]].database_id = message[2][1]

            # "RT" -> remove todo_list from list
            elif message[0] == "RT":
                # remove todo_list
                self.todo_lists.pop(message[1])
                self.notion_todo_lists_hidden.pop(message[1])

                self.dispatch_message(204, ["RT", message[1]])

        # 205 => Update Notion tod_list hidden settings
        elif message_code == 205:
            self.notion_todo_lists_hidden[message[0]] = message[1]

            # remove todo_list from home view
            if message[1]:
                self.dispatch_message(205, message)
            # add calendar to home view
            else:
                if not "send_homepy_todos" in self.threads:
                    # request to send appointments
                    thread = threading.Thread(target=self.send_homepy_todos, daemon=True)
                    thread.start()

                    # add thread to threads dict
                    self.threads.update({"send_homepy_todos": thread})

                    # logging threads
                    self.thread_logger.info(f"started:    [send_homepy_todos] - currently {threading.active_count()} threads open")

        # --- 300 -> Schedule Todos --- #
        # 301 => Schedule Todos Status/requests
        elif message_code == 301:
            # request to schedule todos
            thread = threading.Thread(target=lambda: self.schedule_todos(datetime.now()), daemon=True)

            # keep track of thread
            if not "schedule_todos" in self.threads:
                thread.start()
                self.threads.update({"schedule_todos": thread})

                # logging threads
                self.thread_logger.info(f"started:    [schedule_todos] - currently {threading.active_count()} threads open")

        # --- 400 -> Home.py Requests --- #
        # 401 => Request and send Todos from/for Home.py
        elif message_code == 401:
            if not "send_homepy_todos" in self.threads:
                # request to send appointments
                thread = threading.Thread(target=self.send_homepy_todos, daemon=True)
                thread.start()

                # add thread to threads dict
                self.threads.update({"send_homepy_todos": thread})

                # logging threads
                self.thread_logger.info(f"started:    [send_homepy_todos] - currently {threading.active_count()} threads open")

        # 402 => Request and send Calendar Appointments from/for Home.py
        elif message_code == 402:
            # send homepy appointments
            if not "send_homepy_appointments" in self.threads:
                # request to send appointments
                thread = threading.Thread(target=lambda: self.send_homepy_appointments(self.calendar_span), daemon=True)
                thread.start()
                self.threads.update({"send_homepy_appointments": thread})

                # logging threads
                self.thread_logger.info(f"started:    [send_homepy_appointments] - currently {threading.active_count()} threads open")

        # 403 => Update Todos
        elif message_code == 403:
            # "AT" -> Update todos specifications
            if message[0] == "AT":
                thread = threading.Thread(target=lambda: self.dispatch_message(16, ["AT", message[1],  message[2], self.todo_lists[message[1]].add_task(message[2])]), daemon=True)
                thread.start()

                # add thread to threads dict
                counter = 0
                while True:
                    if not f"add todo {counter}" in self.threads:
                        self.threads.update({f"add todo {counter}": thread})

                        # logging threads
                        self.thread_logger.info(f"started:    [add todo {counter}] - currently {threading.active_count()} threads open")
                        break

            # "CT" -> set todo_state to done (check todo_)
            elif message[0] == "CT":
                thread = threading.Thread(target=lambda: (
                    # reschedule todos
                    self.update_schedule_calendar_for_done_todo(message[2]),
                    # send calendars
                    self.dispatch_message(402, {"done todos": [self.done_todo_calendar, None]}),
                    self.dispatch_message(402, {"scheduled todos": self.get_todo_calendar()}),
                ), daemon=True)
                thread.start()

                # add thread to threads dict
                counter = 0
                while True:
                    if not f"set todo_state to done {counter}" in self.threads:
                        self.threads.update({f"set todo_state to done {counter}": thread})

                        # logging threads
                        self.thread_logger.info(f"started:    [set todo_state to done {counter}] - currently {threading.active_count()} threads open")
                        break

        # 404 => Active Todos --> will not do anything | one way communication pass
        elif message_code == 404:
            pass

        # 405 => Update scheduling todos button label --> will not do anything | one way communication pass
        elif message_code == 405:
            pass

        # 406 => Update schedule order
        elif message_code == 406:
            # "MU" -> move appointment up
            if message[0] == "MU":
                self.move_scheduled_todo_up(message[1])

            # "MD" -> move appointment down
            if message[0] == "MD":
                self.move_scheduled_todo_down(message[1])

            # "LO" -> lock appointment
            if message[0] == "LO":
                self.lock_todo(message[1])

        # --- 600 -> close program --- #
        # 601 => save config to config.py
        elif message_code == 601:
            thread = threading.Thread(target=self.save_config)
            thread.start()

            self.threads.update({f"save config": thread})

            # logging threads
            self.thread_logger.info(f"started:    [save config] - currently {threading.active_count()} threads open")

    def get_calendar_list(self):
        # log function
        self.func_logger.info("[backend] - get calendar list")

        # get calendar list
        try:
            while True:
                # execute function if the integration is ot requesting anything right now
                if not self.google_calendar_integration.requesting:
                    self.calendar_list = self.google_calendar_integration.get_calendars()
                    break
                # wait for the integration to be done requesting
                else:
                    time.sleep(0.3)

            self.google_calendar_connection_status = True
        # error when trying to get calendar list
        except:
            self.google_calendar_connection_status = False

            self.calendar_list = []

    def connect_to_integrations(self):
        # log function
        self.func_logger.info("[backend] - connect to integrations")

        # create google calendar integration
        self.google_calendar_integration = Google_Calendar_Integration(self.dispatch_message)

        # create token request button if it does not exist
        if self.google_calendar_integration.creds is None:
            self.google_calendar_connection_status = False

        # valid creds are existing
        else:
            self.google_calendar_connection_status = True

        # establish Notion Todo_list integration
        for key, todo_list in self.notion_todo_lists.items():
            self.todo_lists.update({key: Notion_Todo_List_Integration(todo_list, self.notion_integration_secret)})

        # send todo_calendar
        self.load_calendars(todos_calendar, done_todos_calendar)

        # update home.py with todos and appointments
        self.send_homepy_appointments([datetime.today() - timedelta(days=10), datetime.today() + timedelta(days=20)])
        self.dispatch_message(405, "Schedule Todos")

    def load_calendars(self, todo_calendar, done_todo_calendar):
        self.done_todo_calendar = done_todo_calendar

        # get appointments and todos
        todo_lists = self.get_todos()

        # clean up todo_lists
        todos = []
        for _, todo_list in todo_lists.items():
            todos += todo_list

        # filter todo_calendar
        todo_calendar = [todo for todo in todo_calendar if todo[2] > datetime.now()]

        for todo in todo_calendar[:]:
            # todo_has been set done
            if "Done" == list(self.todo_lists.values())[0].get_todo_status(todo[4]):
                done_todo_calendar.append(todo)
                todo_calendar.remove(todo)

        if len(todo_calendar) > 0:
            # assign appointments to respective todo_
            for todo in todo_calendar:
                if self.todos[todo[4]]["appointments"] is None:
                    self.todos[todo[4]]["appointments"] = []

                self.todos[todo[4]]["appointments"].append([todo[1], todo[2]])

                # set current todo_to active todo_
                if todo[1] <= datetime.now() <= todo[2]:
                    self.set_active_todo([self.todos[todo[4]]["todo list"], todo[4]])

            # assign order indexes
            sorted_todos = sorted([[key, todo] for key, todo in self.todos.items() if todo["appointments"] is not None], key=lambda x: x[1]["appointments"][0][0])
            for i, todo in enumerate(sorted_todos):
                self.todos[todo[0]]["order index"] = i

            # create todo_calendar
            self.todo_calendar, locks = self.get_todo_calendar()

            # create thread that executes before appointment ist done
            thread = threading.Timer((self.todo_calendar[0][2] - datetime.now()).total_seconds(), self.update_schedule_calendar_at_event_end)
            thread.start()

            self.threads.update({"time till scheduled event ends": thread})

            # logging threads
            self.thread_logger.info(f"started:    [time till scheduled event ends] - currently {threading.active_count()} threads open")

        # no scheduled todos to load
        else:
            self.todo_calendar = []
            locks = []

        # send message to homepy
        self.dispatch_message(402, {"done todos": [self.done_todo_calendar, None], "scheduled todos": [self.todo_calendar, locks]})

    def save_config(self):
        while "connection thread" in self.threads:
            time.sleep(1)

        # log function
        self.func_logger.info("[backend] - save config.py")

        # config object
        config = {
            "google_calendars": self.google_calendars,
            "notion_integration_secret": self.notion_integration_secret,
            "notion_todo_lists": {key: value.database_id for key, value in self.todo_lists.items()},
            "notion_todo_lists_hidden": self.notion_todo_lists_hidden
        }

        # dump json
        with open("Data/config.json", "w") as config_json:
            json.dump(config, config_json)

        # turn datetime to string for json
        clean_todo_calendar = [[app[0], app[1].isoformat(), app[2].isoformat(), app[3], app[4]] for app in self.get_todo_calendar()[0]]
        clean_done_todo_calendar = [[app[0], app[1].isoformat(), app[2].isoformat(), app[3], app[4]] for app in self.done_todo_calendar]

        # calendar data object
        calendar_data = {
            "todos_calendar": clean_todo_calendar,
            "done_todos_calendar": clean_done_todo_calendar
        }

        # dump json
        with open("Data/calendar_data.json", "w") as calendar_data_json:
            json.dump(calendar_data, calendar_data_json)
