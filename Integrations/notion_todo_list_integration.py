import requests

class Notion_Todo_List_Integration(object):
    def __init__(self, database_id, notion_integration_secret):
        self.database_id = database_id
        self.notion_integration_secret = notion_integration_secret
        self.json = None

        self.open_tasks = []

        self.headers = {
            "Accept": "application/json",
            "Authorization": "Bearer " + self.notion_integration_secret,
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        self.max_task_amount = 50

        self.requesting = False

    def update_notion_integration_secret(self, new_secret):
        self.notion_integration_secret = new_secret

        self.headers = {
            "Accept": "application/json",
            "Authorization": "Bearer " + self.notion_integration_secret,
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

    def get_open_tasks(self):
        # set requesting state to true, and start your request
        self.requesting = True

        self.open_tasks.clear()

        # filter to only retrieve open tasks
        filter_object = {
            "or":
                [
                    {
                        "property": "status",
                        "select": {"equals": "Not started"}
                    },
                    {
                        "property": "status",
                        "select": {"equals": "In progress"}
                    }
                ]
        }

        # get database entry's (task's)
        url = f"https://api.notion.com/v1/databases/{self.database_id}/query"

        payload = {"page_size": self.max_task_amount, "filter": filter_object}
        response = requests.post(url, json=payload, headers=self.headers)

        self.json = response.json()

        # extract important data
        for task in self.json["results"]:
            self.open_tasks.append([
                task["properties"]["title"]["title"][0]["text"]["content"],   # retrieve title
                task["properties"]["est. time"]["number"],                    # retrieve estimated time
                task["properties"]["priority"]["number"],                     # retrieve priority
                task["id"]                                                    # retrieve task id
            ])

        # set requesting state to false, request complete
        self.requesting = False

        return self.open_tasks

    def get_todo_status(self, todo_id):
        # get database page
        url = f"https://api.notion.com/v1/pages/{todo_id}"

        response = requests.get(url, headers=self.headers)

        # return success or no success
        if response.status_code == 200:
            return response.json()["properties"]["status"]["select"]["name"]
        else:
            return False

    def set_task_status_to_done(self, task):
        # update open task data
        self.get_open_tasks()

        # update date to set Status to Done
        update_data = {
            "properties": {
                "status": {"select": {"name": "Done"}}
            }
        }

        # get row id
        row_id = task[3]

        # only continue if there is a row id given
        if row_id is not None:
            url = f"https://api.notion.com/v1/pages/{row_id}"

            # Send PATCH request to update the status property of the specific row
            response = requests.patch(url, json=update_data, headers=self.headers)
        # no such task
        else:
            print(f"no task with name {task[0]}")

    def add_task(self, task_name):
        # Data for the new row
        new_row_data = {
            "parent": {"database_id": self.database_id},
            "properties": {
                'status': {'select': {'name': 'Not started'}},
                'est. time': {'number': None},
                'title': {'title': [{'text': {'content': task_name}}]}
            }
        }

        # Send POST request to add a new row
        url = "https://api.notion.com/v1/pages"
        response = requests.post(url, json=new_row_data, headers=self.headers)

        return response.json()["id"], response.status_code

