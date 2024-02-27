import requests

class Notion_Tasklist(object):
    NOTION_INTEGRATION_SECRET = ""

    def __init__(self, database_id):
        self.database_id = database_id
        self.json = None

        self.open_tasks = []

        self.headers = {
            "Accept": "application/json",
            "Authorization": "Bearer " + self.NOTION_INTEGRATION_SECRET,
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        self.max_task_amount = 50

        # get database Data via the Notion API
        self.get_open_tasks()

    def get_open_tasks(self):
        # filter to only retrieve open tasks
        filter_object = {
            "or":
                [
                    {
                        "property": "Status",
                        "status": {"equals": "Not started"}
                    },
                    {
                        "property": "Status",
                        "status": {"equals": "In progress"}
                    },
                    {
                        "property": "Status",
                        "status": {"equals": "Working on"}
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
            ])


