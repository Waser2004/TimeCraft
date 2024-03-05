from notion_api import Notion_Tasklist
from calendar_api import Calendar_Integration
from config import notion_integration_secret

# collect task's from multiple todo_list's
private_todos = Notion_Tasklist("792c7e048ee04c7897941e262f6d4ad1", notion_integration_secret)
school_todos = Notion_Tasklist("fb4af2ee5dad41678d0cb6bc0a277985", notion_integration_secret)

# combine task's
todos = private_todos.open_tasks + school_todos.open_tasks

# collect appointments from multiple calendars
private_calendar = Calendar_Integration("outlook")
school_calendar = Calendar_Integration("url", 'URL')

# combine appointments
appointments = private_calendar.appointments + school_calendar.appointments


print(todos, appointments)