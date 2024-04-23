from Routes.Tkinter_Elemts import checkbox, circle, entry, line, image, rectangle, text
from tkinter import NW
from math import floor
import logging

from config import notion_todo_lists, notion_todo_lists_hidden, notion_integration_secret


class Integrations_Todo_List(object):
    notion_start_todo_lists = notion_todo_lists
    notion_start_todo_lists_hidden = notion_todo_lists_hidden

    func_logger = logging.getLogger("func_logger")

    def __init__(self, root, canvas, window_size):
        self.root = root
        self.canvas = canvas
        self.win_size = window_size

        # scroll
        self.y_scroll = 0

        # order of the visualisation
        self.order = []

        # create notion todo_list blocks
        self.notion_todo_list_blocks = {}
        for (key, value), hidden in zip(self.notion_start_todo_lists.items(), self.notion_start_todo_lists_hidden.values()):
            self.notion_todo_list_blocks.update({key: Notion_Todo_List_Block(self, self.root, self.canvas, self.win_size, key, value, hidden)})
            self.order.append(key)

        left_x = (self.win_size[0] - 300) / 2
        # add new notion todo_list elements
        self.add_url_calendar_plus_1 = line.Line(self.canvas, [left_x + 25, - self.y_scroll + 25 + len(self.notion_todo_list_blocks) * 97 + 37], [left_x + 49, - self.y_scroll + 25 + len(self.notion_todo_list_blocks) * 97 + 37], [64, 71, 79], 1)
        self.add_url_calendar_plus_2 = line.Line(self.canvas, [left_x + 37, - self.y_scroll + 25 + len(self.notion_todo_list_blocks) * 97 + 25], [left_x + 37, - self.y_scroll + 25 + len(self.notion_todo_list_blocks) * 97 + 49],[64, 71, 79], 1)
        self.add_url_calendar_label = text.Text(self.canvas, "add new Notion todo list", [left_x + 64, - self.y_scroll + 25 + len(self.notion_todo_list_blocks) * 97 + 37],[64, 71, 79], 15, anchor="w")

        # notion secret button
        self.notion_secret_background = rectangle.Rectangle(
            self.canvas,
            [self.win_size[0] - 50, self.win_size[1] - 50],
            [self.win_size[0] - 10, self.win_size[1] - 10],
            6,
            [37, 41, 45],
            0,
            [41, 46, 50]
        )
        self.notion_secret_img = image.Tk_Image(self.canvas, [self.win_size[0] - 29, self.win_size[1] - 29], "Assets/notion_logo.png", anchor="center")

        self.notion_secret_popup = Notion_Secret_Popup(self.root, self.canvas, self.win_size)

        if self.notion_secret_popup.notion_integration_secret == "":
            self.notion_secret_popup.draw_state = True

        # update y pos
        self.update_y_pos()

    # update y
    def update_y_pos(self):
        # update y scroll if needed
        if self.y_scroll >= (len(self.notion_todo_list_blocks) + 1) * 97 - self.win_size[1]:
            # set scroll to max
            if (len(self.notion_todo_list_blocks) + 1) * 97 - self.win_size[1] >= 0:
                self.y_scroll = (len(self.notion_todo_list_blocks) + 1) * 97 - self.win_size[1]
            # no more scroll needed
            else:
                self.y_scroll = 0

        # update y pos for url calendar blocks
        for i, key in enumerate(self.order):
            self.notion_todo_list_blocks[key].set_y_pos(- self.y_scroll + 25 + i * 97)

        left_x = (self.win_size[0] - 300) / 2
        self.add_url_calendar_plus_1.set_pos([left_x + 25, - self.y_scroll + 25 + len(self.notion_todo_list_blocks) * 97 + 37],[left_x + 49, - self.y_scroll + 25 + len(self.notion_todo_list_blocks) * 97 + 37])
        self.add_url_calendar_plus_2.set_pos([left_x + 37, - self.y_scroll + 25 + len(self.notion_todo_list_blocks) * 97 + 25],[left_x + 37, - self.y_scroll + 25 + len(self.notion_todo_list_blocks) * 97 + 49])
        self.add_url_calendar_label.set_center([left_x + 64, - self.y_scroll + 25 + len(self.notion_todo_list_blocks) * 97 + 37])

        # Notion secret button
        self.notion_secret_background.set_pos([self.win_size[0] - 50, self.win_size[1] - 50], [self.win_size[0] - 10, self.win_size[1] - 10])
        self.notion_secret_img.set_center([self.win_size[0] - 29, self.win_size[1] - 29])

        self.notion_secret_popup.set_win_size(self.win_size)

    # delete url block
    def delete_notion_block(self, key):
        # delete block
        self.notion_todo_list_blocks[key].delete()
        self.notion_todo_list_blocks.pop(key)
        self.order.remove(key)

        # update y pos
        self.update_y_pos()

        # send message to remove url calendar from backend
        self.dispatch_message(204, ["RT", key])

    def add_notion_block(self, key):
        self.notion_todo_list_blocks.update({key: Notion_Todo_List_Block(self, self.root, self.canvas, self.win_size, key, "", False)})
        self.notion_todo_list_blocks[key].draw()
        self.notion_todo_list_blocks[key].set_backend_connection(self.dispatch_message)
        self.order.append(key)

        self.update_y_pos()

    def set_notion_todo_list_statuses(self, statuses):
        if len(statuses) == len(self.notion_todo_list_blocks):
            for (_, block), status in zip(self.notion_todo_list_blocks.items(), statuses):
                block.set_status(status)

    # -------------------------
    # drawing/erasing functions
    # -------------------------
    def draw(self):
        # notion todo_list block
        for _, block in self.notion_todo_list_blocks.items():
            block.draw()

        self.add_url_calendar_plus_1.draw()
        self.add_url_calendar_plus_2.draw()
        self.add_url_calendar_label.draw()

        self.notion_secret_background.draw()
        self.notion_secret_img.draw()

        if self.notion_secret_popup.draw_state or self.notion_secret_popup.notion_integration_secret == "":
            self.notion_secret_popup.draw_state = True
            self.notion_secret_popup.draw()

    def delete(self):
        # notion todo_list block
        for _, block in self.notion_todo_list_blocks.items():
            block.delete()

        self.add_url_calendar_plus_1.delete()
        self.add_url_calendar_plus_2.delete()
        self.add_url_calendar_label.delete()

        self.notion_secret_background.delete()
        self.notion_secret_img.delete()

        self.notion_secret_popup.delete()

    # --------------------------------------
    # handle front and backend communication
    # --------------------------------------
    def set_backend_connection(self, backend_connection):
        self.dispatch_message = backend_connection

        self.notion_secret_popup.set_backend_connection(backend_connection)

        for _, block in self.notion_todo_list_blocks.items():
            block.set_backend_connection(backend_connection)

    # -------------
    # window events
    # -------------
    # window resize
    def resize(self, event):
        # set win size
        self.win_size = [event.width, event.height]

        # resize blocks
        for i, (_, block) in enumerate(self.notion_todo_list_blocks.items()):
            block.resize(event)

        # update y pos
        self.update_y_pos()

    # left click
    def mouse_left_click(self, event):
        # notion secret popup is not open
        if not self.notion_secret_popup.draw_state:
            # notion todo_list block
            for _, block in self.notion_todo_list_blocks.items():
                block.mouse_left_click(event)

            # add new calendar clicked
            left_x = (self.win_size[0] - 300) / 2

            if left_x <= event.x <= left_x + 600 and 25 + len(self.notion_todo_list_blocks) * 97 <= event.y <= 25 + len(self.notion_todo_list_blocks) * 97 + 74:
                self.dispatch_message(204, ["AT", "new notion todo list"])

            # notion secret button
            if self.notion_secret_background.is_pressed(event.x, event.y):
                self.notion_secret_popup.draw_state = True
                self.notion_secret_popup.draw()

        # notion secret popup is open
        else:
            # popup press
            self.notion_secret_popup.mouse_left_click(event)

            # notion secret button
            if self.notion_secret_background.is_pressed(event.x, event.y) and self.notion_secret_popup.notion_integration_secret != "":
                self.notion_secret_popup.draw_state = False
                self.notion_secret_popup.entry.set_text(self.notion_secret_popup.notion_integration_secret)
                self.notion_secret_popup.submit_label.set_text("save")
                self.notion_secret_popup.delete()

    # right click
    def mouse_right_click(self, event):
        # notion todo_list block
        for _, block in self.notion_todo_list_blocks.items():
            block.mouse_left_click(event)

    # mouse movement
    def mouse_movement(self, event):
        # notion todo_list block
        for _, block in self.notion_todo_list_blocks.items():
            block.mouse_movement(event)
    
    def mouse_wheel(self, event):
        # scroll
        if (len(self.notion_todo_list_blocks) + 1) * 97 > self.win_size[1]:
            # scroll up
            if self.y_scroll + 10 <= (len(self.notion_todo_list_blocks) + 1) * 97 - self.win_size[1] and event.delta < 0:
                self.y_scroll += 10
            # set to max scroll
            elif event.delta < 0:
                self.y_scroll = (len(self.notion_todo_list_blocks) + 1) * 97 - self.win_size[1]

            # scroll down
            elif self.y_scroll - 10 >= 0 and event.delta > 0:
                self.y_scroll -= 10
            # set to min scroll
            elif event.delta > 0:
                self.y_scroll = 0

            self.update_y_pos()


########################################################################################################################
# Notion Todolist block
########################################################################################################################
class Notion_Todo_List_Block(object):
    def __init__(self, parent, root, canvas, window_size, todo_list_name, todo_list_key, hidden):
        self.parent = parent
        self.root = root
        self.win_size = window_size
        self.canvas = canvas

        # block specifics
        self.todo_list_name = todo_list_name
        self.todo_list_key = todo_list_key
        self.hidden = hidden

        # y_pos
        self.y_pos = 0

        left_x = (self.win_size[0] - 300) / 2
        # create elements
        # Title
        self.title = text.Text(self.canvas, f"Notion todo list - ", [left_x, 20 + self.y_pos], [230, 230, 230], 20, anchor=NW)
        self.title_entry = entry.Entry(self.root, self.canvas, self.todo_list_name, [left_x + 162, 20 + self.y_pos], 374,[46, 51, 56], [230, 230, 230], 20, placeholder="No Name - please set a name")
        self.title_entry.bind_change = self.calendar_info_changed
        # URL
        self.key_label = text.Text(self.canvas, f"Key:", [left_x, 56 + self.y_pos], [130, 130, 130], 15, anchor=NW)
        self.key_entry = entry.Entry(self.root, self.canvas, self.todo_list_key, [left_x + 34, 56 + self.y_pos], 496, [46, 51, 56], [130, 130, 130], 15, placeholder="No database key - please enter key")
        self.key_entry.bind_change = self.calendar_info_changed
        # hide button
        self.hide_button = image.Tk_Image(self.canvas, [left_x + 543, 41 + self.y_pos], "Assets/eye_view.png")
        # delete button
        self.delete_button = image.Tk_Image(self.canvas, [left_x + 574, 40 + self.y_pos], "Assets/trash_bin_white.png")
        # spacer line
        self.spacer = line.Line(self.canvas, [left_x, 95 + self.y_pos], [left_x + 600, 95 + self.y_pos], [64, 71, 79],1)

        # status indication
        self.status = None
        self.status_indicator = None

        self.set_hidden_state(self.hidden)

    def set_y_pos(self, y):
        self.y_pos = y

        # update positions
        left_x = (self.win_size[0] - 300) / 2
        # update positions
        self.title.set_center([left_x, 20 + self.y_pos])
        self.title_entry.set_corner_1([left_x + 162, 20 + self.y_pos])
        self.key_label.set_center([left_x, 56 + self.y_pos])
        self.key_entry.set_corner_1([left_x + 34, 56 + self.y_pos])
        self.hide_button.set_center([left_x + 543, 41 + self.y_pos])
        self.delete_button.set_center([left_x + 574, 40 + self.y_pos])
        self.spacer.set_pos([left_x, 95 + self.y_pos], [left_x + 600, 95 + self.y_pos])

        # update status indicator
        if self.status_indicator is not None:
            self.status_indicator.set_center([left_x - 40, 40 + self.y_pos])

    def set_status(self, status):
        self.status = status

        # create error indicator
        if not self.status:
            self.status_indicator = image.Tk_Image(self.canvas, [(self.win_size[0] - 300) / 2 - 40, 40 + self.y_pos], "Assets/error_yellow.png")
        # remove error indicator
        elif self.status_indicator is not None:
            self.status_indicator.delete()
            self.status_indicator = None

    def set_hidden_state(self, hidden: bool):
        # hide calendar block
        if hidden:
            # update parameter
            self.hidden = True

            # update looks
            self.hide_button.set_img("Assets/eye_hide.png")
            self.title.set_color([130, 130, 130])
            self.title_entry.set_color([130, 130, 130])

            self.key_label.set_color([75, 75, 75])
            self.key_entry.set_color([75, 75, 75])

        # show calendar block
        else:
            # update parameter
            self.hidden = False

            # update looks
            self.hide_button.set_img("Assets/eye_view.png")
            self.title.set_color([230, 230, 230])
            self.title_entry.set_color([230, 230, 230])

            self.key_label.set_color([130, 130, 130])
            self.key_entry.set_color([130, 130, 130])

    # -------------
    # entry changes
    # -------------
    def calendar_info_changed(self, _):
        # dispatch message
        self.dispatch_message(204, ["UT", self.todo_list_name, [self.title_entry.txt, self.key_entry.txt]])

        self.todo_list_name = self.title_entry.txt
        self.todo_list_key = self.key_entry.txt

    # --------------------------------------
    # handle front and backend communication
    # --------------------------------------
    def set_backend_connection(self, backend_connection):
        self.dispatch_message = backend_connection

    # -------------------------
    # drawing/erasing functions
    # -------------------------
    def draw(self):
        self.title.draw()
        self.title_entry.draw()
        self.key_label.draw()
        self.key_entry.draw()
        self.hide_button.draw()
        self.delete_button.draw()
        self.spacer.draw()

        # update status indicator
        if self.status_indicator is not None:
            self.status_indicator.draw()

    def delete(self):
        self.title.delete()
        self.title_entry.delete()
        self.key_label.delete()
        self.key_entry.delete()
        self.hide_button.delete()
        self.delete_button.delete()
        self.spacer.delete()

        # update status indicator
        if self.status_indicator is not None:
            self.status_indicator.delete()

    # -------------
    # window events
    # -------------
    # window resize
    def resize(self, event):
        self.win_size = [event.width, event.height]

    # left click
    def mouse_left_click(self, event):
        if self.delete_button.is_pressed(event):
            self.parent.delete_notion_block(self.todo_list_name)

        # hide button press - hide calendar
        if self.hide_button.is_pressed(event):
            self.set_hidden_state(False if self.hidden else True)

            # dispatch message of changed hidden state
            self.dispatch_message(205, [self.todo_list_name, self.hidden])

    # right click
    def mouse_right_click(self, event):
        pass

    def mouse_movement(self, event):
        # hover over - change to red
        if self.delete_button.is_pressed(event) and self.delete_button.src == "Assets/trash_bin_white.png":
            self.delete_button.set_img("Assets/trash_bin_red.png")

        # no longer hove - change to white
        elif not self.delete_button.is_pressed(event) and self.delete_button.src == "Assets/trash_bin_red.png":
            self.delete_button.set_img("Assets/trash_bin_white.png")

class Notion_Secret_Popup(object):
    def __init__(self, root, canvas, win_size):
        # set parameters
        self.root = root
        self.canvas = canvas
        self.win_size = win_size

        self.draw_state = False
        self.dispatch_message = None

        self.notion_integration_secret = notion_integration_secret

        # create canvas elements
        left_x, left_y = (self.win_size[0] - 300) / 2 + 100, self.win_size[1] / 2 - 100
        self.background = rectangle.Rectangle(
            self.canvas,
            [floor(left_x), floor(left_y)],
            [floor(left_x + 400), floor(left_y + 200)],
            10,
            [37, 41, 45],
            0,
            [37, 41, 45]
        )
        self.title = text.Text(
            self.canvas,
            "Notion integration secret:",
            [left_x + 20, left_y + 20],
            [230, 230, 230],
            font_size=20,
            anchor="nw"
        )
        self.entry = entry.Entry(
            self.root,
            self.canvas,
            self.notion_integration_secret,
            [left_x + 20, left_y + 100],
            360,
            [37, 41, 45],
            [230, 230, 230],
            placeholder="set notion integration secret",
            text_fill_char=" *"
        )
        self.submit_button = rectangle.Rectangle(
            self.canvas,
            [floor(left_x + 20), floor(left_y + 140)],
            [floor(left_x + 380), floor(left_y + 180)],
            6,
            [83, 191, 102],
            0,
            [83, 191, 102]
        )
        self.submit_label = text.Text(
            self.canvas,
            "save",
            [floor(left_x + 200), floor(left_y + 160)],
            [230, 230, 230],
            font_size=15
        )
        self.pop_up_cross_p1 = line.Line(
            self.canvas,
            [left_x + 360, left_y + 20],
            [left_x + 380, left_y + 40],
            [46, 51, 56],
            2
        )
        self.pop_up_cross_p2 = line.Line(
            self.canvas,
            [left_x + 380, left_y + 20],
            [left_x + 360, left_y + 40],
            [46, 51, 56],
            2
        )

    # --------------------------------------
    # handle front and backend communication
    # --------------------------------------
    def set_backend_connection(self, backend_connection):
        self.dispatch_message = backend_connection

    # -------------------------
    # drawing/erasing functions
    # -------------------------
    # draw
    def draw(self):
        self.background.draw()
        self.title.draw()
        self.entry.draw()
        self.submit_button.draw()
        self.submit_label.draw()
        self.pop_up_cross_p1.draw()
        self.pop_up_cross_p2.draw()

        self.canvas.tag_raise(self.background.object)
        self.canvas.tag_raise(self.title.object)
        self.canvas.tag_raise(self.entry.text.object)
        self.canvas.tag_raise(self.submit_button.object)
        self.canvas.tag_raise(self.submit_label.object)
        self.canvas.tag_raise(self.pop_up_cross_p1.object)
        self.canvas.tag_raise(self.pop_up_cross_p2.object)

    # delete
    def delete(self):
        self.background.delete()
        self.title.delete()
        self.entry.delete()
        self.submit_button.delete()
        self.submit_label.delete()
        self.pop_up_cross_p1.delete()
        self.pop_up_cross_p2.delete()

    # update
    def update(self):
        left_x, left_y = (self.win_size[0] - 300) / 2 + 100, self.win_size[1] / 2 - 100
        self.background.set_pos([floor(left_x), floor(left_y)], [floor(left_x + 400), floor(left_y + 200)])
        self.title.set_center([left_x + 20, left_y + 20])
        self.entry.set_corner_1([left_x + 20, left_y + 100])
        self.submit_button.set_pos([floor(left_x + 20), floor(left_y + 140)], [floor(left_x + 380), floor(left_y + 180)])
        self.submit_label.set_center([floor(left_x + 200), floor(left_y + 160)])
        self.pop_up_cross_p1.set_pos([left_x + 360, left_y + 20], [left_x + 380, left_y + 40])
        self.pop_up_cross_p2.set_pos([left_x + 380, left_y + 20], [left_x + 360, left_y + 40])

    # -------------------------
    # drawing/erasing functions
    # -------------------------
    def set_win_size(self, win_size):
        self.win_size = win_size

        self.update()

    # mouse event
    def mouse_left_click(self, event):
        left_x, left_y = (self.win_size[0] - 300) / 2 + 100, self.win_size[1] / 2 - 100

        # close popup
        if left_x + 360 <= event.x <= left_x + 380 and left_y + 20 <= event.y <= left_y + 40 or \
                (not self.background.is_pressed(event.x, event.y) and self.notion_integration_secret):
            self.draw_state = False
            self.entry.set_text(self.notion_integration_secret)
            self.submit_label.set_text("save")
            self.delete()

        # save button is saved
        elif self.submit_button.is_pressed(event.x, event.y):
            self.notion_integration_secret = self.entry.txt
            self.submit_label.set_text("save")

            self.dispatch_message(201, self.notion_integration_secret)

