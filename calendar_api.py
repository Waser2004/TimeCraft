import datetime
import requests
from win32com.client import Dispatch
from ics import Calendar

test_datetime = datetime.datetime(2024, 3, 20, 8, 0)

class Calendar_Integration(object):
    def __init__(self, calendar_type, calendar_url: str = None):
        self.calendar_type = calendar_type
        self.calendar_url = calendar_url

        self.appointments = []

        self.timespan = 5

        # collect Outlook appointments
        if self.calendar_type == "outlook":
            self.get_outlook_appointments()
        # collect linked Calendar appointments
        elif self.calendar_type == "url":
            self.get_url_calendar_appointments()

    def get_outlook_appointments(self):
        # Connect to Outlook
        outlook = Dispatch("Outlook.Application")
        ns = outlook.GetNamespace("MAPI")

        # Get appointments
        appointments = ns.GetDefaultFolder(9).Items
        appointments.IncludeRecurrences = True

        # sort appointments
        appointments.Sort("[Start]")
        appointments = list(appointments)
        appointments.reverse()

        now = test_datetime

        # Iterate through each item in the Calendar folder
        for item in appointments:
            # only get appointments from now until 20 days in the future
            item_end_date = datetime.datetime.fromisoformat(str(item.End)).replace(tzinfo=None)

            if now <= item_end_date < now + datetime.timedelta(days = 20):
                self.appointments.append([
                    item.Subject,                                                                 # title
                    datetime.datetime.fromisoformat(str(item.Start)).replace(tzinfo=None),        # start time
                    datetime.datetime.fromisoformat(str(item.End)).replace(tzinfo=None),          # end time
                    item.Location                                                                 # location
                ])

            # end loop for appointments in the past
            elif item_end_date < now:
                break

    def get_url_calendar_appointments(self):
        # Fetch the calendar data from the URL
        response = requests.get(self.calendar_url)

        if response.status_code == 200:
            # Parse the calendar data
            calendar = Calendar(response.text)

            now = test_datetime

            # Iterate through each item in the Calendar folder
            sorted_events = sorted(calendar.events, key=lambda event: event.begin)
            for event in reversed(sorted_events):
                # only get appointments from now until 20 days in the future
                item_end_date  = datetime.datetime.fromisoformat(str(event.end)).replace(tzinfo=None)

                if now <= item_end_date < now + datetime.timedelta(days=20):
                    self.appointments.append([
                        event.name,                                                                 # title
                        datetime.datetime.fromisoformat(str(event.begin)).replace(tzinfo=None),     # start time
                        datetime.datetime.fromisoformat(str(event.end)).replace(tzinfo=None),       # end time
                        event.location                                                              # location
                    ])

                # end loop for appointments in the past
                elif item_end_date < now:
                    break
        else:
            print(f"Failed to fetch calendar data. Status code: {response.status_code}")