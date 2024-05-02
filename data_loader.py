import json
import os.path
from datetime import datetime

if os.path.exists("Data/config.json"):
    # load config json
    with open("Data/config.json", "r") as config_json:
        config_data = json.load(config_json)

        # write data to variables
        google_calendars = config_data["google_calendars"]
        notion_integration_secret = config_data["notion_integration_secret"]
        notion_todo_lists = config_data["notion_todo_lists"]
        notion_todo_lists_hidden = config_data["notion_todo_lists_hidden"]

# no config file yet
else:
    # create variables
    google_calendars = {}
    notion_integration_secret = ""
    notion_todo_lists = {}
    notion_todo_lists_hidden = {}

if os.path.exists("Data/calendar_data.json"):
    # load calendar_data json
    with open("Data/calendar_data.json", "r") as calendar_data_json:
        calendar_data_data = json.load(calendar_data_json)

        # write data to variables
        todos_calendar = calendar_data_data["todos_calendar"]
        done_todos_calendar = calendar_data_data["done_todos_calendar"]

        # turn iso to datetime
        todos_calendar = [[app[0], datetime.fromisoformat(app[1]), datetime.fromisoformat(app[2]), app[3], app[4]] for app in todos_calendar]
        done_todos_calendar = [[app[0], datetime.fromisoformat(app[1]), datetime.fromisoformat(app[2]), app[3], app[4]] for app in done_todos_calendar]

# no calendar data file yet
else:
    # create variables
    todos_calendar = []
    done_todos_calendar = []
