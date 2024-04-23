import logging
import os
import signal
import time

# basic config
logging.basicConfig(
    level=logging.INFO,
    filename="Logs/main.log",
    filemode="w",
    format="%(asctime)s - %(name)s - %(levelname)s -> %(message)s"
)

import threading

from frontend import GUI
from backend import Backend

from config import google_calendars, notion_todo_lists, notion_todo_lists_hidden, notion_integration_secret

# -----------------------------------
# create logger
# -----------------------------------
# create thread log handlers and formatter
thread_handler = logging.FileHandler("Logs/threads.log", mode='w')
formatter = logging.Formatter("%(asctime)s - %(levelname)s -> %(message)s")

# create thread logger
thread_logger = logging.getLogger("thread_log")
thread_logger.setLevel(logging.DEBUG)
thread_handler.setFormatter(formatter)
thread_logger.addHandler(thread_handler)

# create function log handlers
func_handler = logging.FileHandler("Logs/funcs.log", mode='w')

# create function logger
func_logger = logging.getLogger("func_log")
func_logger.setLevel(logging.DEBUG)
func_handler.setFormatter(formatter)
func_logger.addHandler(func_handler)

# logging threads
thread_logger.info("started:    [main thread]")

# -----------------------------------
# create frontend and backend classes
# -----------------------------------
# create frontend
frontend = GUI()
backend = Backend(google_calendars, notion_todo_lists, notion_todo_lists_hidden, notion_integration_secret)

backend.set_frontend_connection(frontend.receive_message)
frontend.set_backend_connection(backend.receive_message)

# create backend
def backend_thread_function():
    # connect to Calendars/Todo_lists
    backend.connect_to_integrations()

def frontend_thread_function():
    frontend.draw()
    frontend.mainloop()

# -----------
# run program
# -----------
if __name__ == '__main__':
    # run threads
    backend_thread = threading.Thread(target=backend_thread_function, daemon=True)

    backend_thread.start()
    backend.threads.update({"connection thread": backend_thread})

    # logging threads
    thread_logger.info(f"started:    [connection thread] - currently {threading.active_count()} threads open")

    frontend_thread_function()

    # when program finished stop backend loop
    if backend.loop_thread is not None:
        if len(backend.loop_thread) > 1:
            backend.loop_thread[0].join()

        backend.loop_thread[-1].cancel()
