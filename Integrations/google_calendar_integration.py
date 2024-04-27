import os.path
import datetime
import time

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

class Google_Calendar_Integration(object):
    SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
    def __init__(self, frontend_connection):
        self.dispatch_message = frontend_connection

        # connect to calendar
        self.get_credentials()
        try:
            self.service = build("calendar", "v3", credentials=self.creds)
        except:
            self.service = None

        self.flow = None

        # requesting state
        self.requesting = False
        self.requesting_token = False

    def set_frontend_connection(self, frontend_connection):
        self.dispatch_message = frontend_connection

    def get_credentials(self):
        # get credentials from file
        if os.path.exists("Integrations/Google_API_Config/token.json"):
            self.creds = Credentials.from_authorized_user_file("Integrations/Google_API_Config/token.json", self.SCOPES)

            # if the creds are expired refresh them
            if not self.creds.expired:
                self.creds.refresh(Request())
        else:
            self.creds = None

    # create token via login page
    def request_token(self):
        # set requesting state to true
        self.requesting_token = True

        self.flow = InstalledAppFlow.from_client_secrets_file(
            "Integrations/Google_API_Config/credentials.json", self.SCOPES,
        )
        # create thread for opening the browser
        self.creds = self.flow.run_local_server(port=0)
        self.service = build("calendar", "v3", credentials=self.creds)

        # Save the credentials for the next run
        with open("Integrations/Google_API_Config/token.json", "w") as token:
            token.write(self.creds.to_json())

        # set requesting state to false, no longer requesting information
        self.requesting_token = False

    def get_appointments(self, calendar_id, timespan: [datetime.datetime, datetime.datetime]):
        # set requesting state to true
        self.requesting = True

        appointments = []

        try:
            # set time frame for appointment retrieve
            now = timespan[0].isoformat() + "Z"
            max_time = timespan[1].isoformat() + "Z"

            # get events
            events_result = (
                self.service.events()
                .list(
                    calendarId=calendar_id,
                    timeMin=now,
                    timeMax=max_time,
                    singleEvents=True,
                    orderBy="startTime",
                    timeZone='Europe/Zurich'
                )
                .execute()
            )
            events = events_result.get("items", [])

            # add event to appointment list
            for event in events:
                if "dateTime" in event["start"]:
                    appointments.append([
                        event["summary"],
                        datetime.datetime.fromisoformat(str(event["start"]["dateTime"])[:19]),
                        datetime.datetime.fromisoformat(str(event["end"]["dateTime"])[:19]),
                        event["location"] if "location" in event else None
                    ])

                else:
                    appointments.append([
                        event["summary"],
                        datetime.datetime.fromisoformat(str(event["start"]["date"] + "T00:00:00Z")[:19]),
                        datetime.datetime.fromisoformat(str(event["end"]["date"] + "T23:59:59Z")[:19]) - datetime.timedelta(days=1),
                        event["location"] if "location" in event else None
                    ])

        # error while retrieving data
        except Exception as error:
            # set requesting state to false, no longer requesting information
            self.requesting = False

            raise Exception(f"Connection to the Calendar failed with the error: {error}")

        # set requesting state to false, no longer requesting information
        self.requesting = False


        return appointments

    def get_calendars(self):
        # set requesting state to true
        self.requesting = True

        try:
            # Get a list of calendars
            calendar_list = self.service.calendarList().list().execute()

            # convert calendar information
            calendars = {}
            for calendar_list_entry in calendar_list['items']:
                calendars.update({calendar_list_entry['summary']: calendar_list_entry['id']})
        except:
            calendars = {}

        # set requesting state to false, no longer requesting information
        self.requesting = False

        return calendars