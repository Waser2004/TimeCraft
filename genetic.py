import datetime
import random
import math
from copy import deepcopy
from itertools import permutations
from win32com.client import Dispatch, constants


test_datetime = datetime.datetime(2024, 3, 20, 8, 0)


class Genetic_algorithm(object):
    def __init__(self, tasks, appointments):
        self.tasks = tasks
        self.appointments = sorted(appointments, key=lambda appointment: appointment[1])

        # clean tasks list
        # assign new priorities
        priority_sorted = sorted(self.tasks, key=lambda task:(task[2] is None, task[2]))
        self.tasks = [prio[:2] + [i + 1] for i, prio in enumerate(priority_sorted)]

        # assign estimate time for tasks with None given estimated time
        self.tasks = [[title, est_time if est_time is not None else 0.2, prio] for title, est_time, prio in self.tasks]

        self.evaluation_mode = None
        # create all possible gens
        if 1_000 >= math.factorial(len(self.tasks)):
            self.gens = list(permutations(list(range(len(self.tasks))), len(self.tasks)))
            self.evaluation_mode = "forward"
        # create 1'000 random gens
        else:
            self.gens = [random.sample(range(len(self.tasks)), len(self.tasks)) for _ in range(300)]
            self.evaluation_mode = "genetic"

        # connect to Outlook calendar
        outlook = Dispatch("Outlook.Application")
        ns = outlook.GetNamespace("MAPI")

        try:
            self.calendar = ns.GetDefaultFolder(9).Folders("TimeCraft")
        except:
            self.calendar = ns.GetDefaultFolder(9).Folders.Add("TimeCraft")

        # find best gen
        self.evaluate()

    def evaluate(self):
        # evaluate if all possible variations
        if self.evaluation_mode == "forward":
            # find best solution
            best_solution = [0, self.fitness(self.gens[0])]

            for i, gen in enumerate(self.gens[1:]):
                if (fit := self.fitness(gen)) <= best_solution[1]:
                    best_solution = [i + 1, fit]

            # sort tasks based on given example
            sorted_tasks = [self.tasks[i] for i in self.gens[best_solution[0]]]

            # calculate the start and end time of each task for this order
            timed_tasks = self.calculate_task_times(sorted_tasks, deepcopy(self.appointments))

            print(timed_tasks)

        # genetic algorithm
        elif self.evaluation_mode == "genetic":
            # stat properties
            counter = 0
            prev_score = 0

            # genetic loop
            while counter < 10:
                # rank gens
                ranked_gens = [(self.fitness(gen), gen) for gen in self.gens]
                ranked_gens.sort()

                # best 100 ranked gens
                best_gens = [gen[1] for gen in ranked_gens[:30]]

                # keep best solution
                self.gens.clear()
                self.gens.append(best_gens[0])

                # create new gen
                for _ in range(299):
                    # get random gen index and random seperator index for gen cutting
                    gen_i = random.choice(list(range(len(best_gens))))
                    seperator = random.randint(0, len(best_gens[0]))

                    # calculate cut away indices
                    cut_indices = list(range(len(self.gens[0])))
                    for elm in best_gens[gen_i][:seperator]:
                        cut_indices.remove(elm)

                    random.shuffle(cut_indices)

                    # gen cutting and adding shuffled cut_indices
                    new_gen = best_gens[gen_i][:seperator] + cut_indices

                    # gen mutation (chance of 2% to happen)
                    if random.randint(0, 50) < 1:
                        # select switch indices
                        first_gen = random.choice(list(range(len(best_gens[0]))))
                        second_gen = random.choice(list(range(len(best_gens[0]))))

                        # gen mutation
                        temp = new_gen[first_gen]
                        new_gen[first_gen] = new_gen[second_gen]
                        new_gen[second_gen] = temp

                    # add new gen to gen list
                    self.gens.append(new_gen)

                # keep stats
                if prev_score == ranked_gens[0][0]:
                    counter += 1
                else:
                    counter = 0

                prev_score = ranked_gens[0][0]

            # best solution from genetic algorithm
            best_solution = [0, ranked_gens[0][0]]

            print(best_solution)

        # sort tasks based on given example
        sorted_tasks = [self.tasks[i] for i in self.gens[best_solution[0]]]

        # calculate the start and end time of each task for this order
        timed_tasks = self.calculate_task_times(sorted_tasks, deepcopy(self.appointments))

        # put events into the calendar
        self.create_calendar_appointments(timed_tasks)

    def fitness(self, example):
        score = 0

        # sort tasks based on given example
        sorted_tasks = [self.tasks[i] for i in example]

        # calculate the start and end time of each task for this order
        timed_tasks = self.calculate_task_times(sorted_tasks, deepcopy(self.appointments))

        # evaluate task score
        seconds_to_event_start = [(task[1] - test_datetime).total_seconds() for task in timed_tasks]
        for i, time_offset in enumerate(seconds_to_event_start):
            # score is relative time to task start multiplied with 3/4 of the reversed priorities
            time_value = time_offset / max(seconds_to_event_start) * len(sorted_tasks)
            priority_value = (len(sorted_tasks) - i + 1) ** 1.75

            score += time_value * priority_value

        return score

    def create_calendar_appointments(self, timed_tasks):
        # get existing appointments of the calendar
        appointments = self.calendar.Items

        # sort appointments
        appointments.Sort("[Start]")
        appointments = list(appointments)
        appointments.reverse()

        existing_appointments = []
        now = test_datetime

        # Iterate through each item in the Calendar folder
        for item in appointments:
            # only get appointments from now until 20 days in the future
            item_end_date = datetime.datetime.fromisoformat(str(item.End)).replace(tzinfo=None)

            if now <= item_end_date < now + datetime.timedelta(days=20):

                # check if the existing appointment has the same name as one of the tasks
                if [task[0] for task in timed_tasks].count(item.Subject):
                    existing_appointments.append(item.Subject)

            # end loop for appointments in the past
            elif item_end_date < now:
                break

        # put tasks into the calendar or update existing ones
        for task in timed_tasks:
            # task appointment is existing
            if existing_appointments.count(task[0]):
                appointment = self.calendar.Items(task[0])
                # update appointment end time if it is currently running
                if (start := datetime.datetime.fromisoformat(str(appointment.Start)).replace(tzinfo=None)) < now:
                    appointment.Duration = (task[2] - start).total_seconds() / 60
                # update whole appointment times
                else:
                    appointment.Start = task[1].strftime('%Y-%m-%d %H:%M')
                    appointment.Duration = (task[2] - task[1]).total_seconds() / 60

                # save changes
                appointment.Save()
            # all new task
            else:
                # create new appointment
                appointment = self.calendar.Items.Add(1)
                # set title, start time and duration
                appointment.Subject = task[0]
                appointment.Start = task[1].strftime('%Y-%m-%d %H:%M')
                appointment.Duration = (task[2] - task[1]).total_seconds() / 60
                # save appointment changes
                appointment.Save()

    @staticmethod
    def calculate_task_times(tasks, appointments):
        timed_tasks = []
        time = test_datetime

        # find a valid space for each task
        for task in tasks:
            task_timeframe = [time, time + datetime.timedelta(hours=task[1])]

            while 0 < len(appointments):
                appointment = appointments[0]

                # task fits before appointment
                if task_timeframe[0] <= appointment[1] and task_timeframe[1] <= appointment[1]:
                    timed_tasks.append([task[0]] + task_timeframe)
                    time = task_timeframe[1]

                    break

                # task fits after appointment
                if task_timeframe[0] >= appointment[2] and task_timeframe[1] >= appointment[2]:
                    # task fits before next appointment
                    if task_timeframe[0] <= appointments[1][1] and task_timeframe[1] <= appointments[1][1]:
                        timed_tasks.append([task[0]] + task_timeframe)
                        time = task_timeframe[1]
                        appointments.remove(appointment)

                        break

                # task interferes with appointment
                else:
                    task_timeframe = [appointment[2], appointment[2] + datetime.timedelta(hours=task[1])]
                    appointments.remove(appointment)

        return timed_tasks


