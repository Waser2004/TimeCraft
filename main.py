from Notion_Database import Notion_Tasklist

# collect task's from multiple todo_list's
main_todos = Notion_Tasklist("792c7e048ee04c7897941e262f6d4ad1")     # collect task's from main todo_list
school_todos = Notion_Tasklist("fb4af2ee5dad41678d0cb6bc0a277985")   # collect task's from school todo_list

# combine task's
todos = main_todos.open_tasks + school_todos.open_tasks

print(todos)