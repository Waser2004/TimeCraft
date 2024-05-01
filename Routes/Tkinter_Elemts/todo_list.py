import tkinter as tk
from Routes.Tkinter_Elemts import checkbox, entry, text, line, rectangle

class Todo_List(object):
    def __init__(self, root: tk.Tk, canvas: tk.Canvas, corner_1: [int, int], corner_2: [int, int],
                 text_color: [int, int, int], highlight_color: [int, int, int]):
        self.root = root
        self.canvas = canvas
        self.dispatch_message = None

        # position arguments
        self.corner_1 = corner_1
        self.corner_2 = corner_2
        self.y_scroll = 0
        self.height = 0

        # colors
        self.text_color = text_color
        self.highlight_color = highlight_color

        # todolist window elements
        self.todo_list_blocks = {}
        self.order = []

        # active todo_indicator
        self.active_todo = None

        # label for no todolist
        color = [self.text_color[0] * 0.65, self.text_color[1] * 0.65, self.text_color[2] * 0.65]
        self.no_todolist_label = text.Text(self.canvas, "No Todo-lists found", self.corner_1, color, 20, anchor="nw")

        self.draw_status = False

    def set_backend_connection(self, backend_connection):
        self.dispatch_message = backend_connection

    # ---------------------------
    # update todo_list parameters
    # ---------------------------
    def add_todo_list(self, todo_list_name, todos):
        self.todo_list_blocks.update({
            todo_list_name: Todo_List_Block(
                self, self.root, self.canvas, self.corner_1, self.corner_2, self.y_scroll, self.text_color,
                self.highlight_color, todo_list_name, todos
            )
        })

        self.order.append(todo_list_name)

        self.update()

    def remove_todo_list(self, todo_list_name):
        self.todo_list_blocks[todo_list_name].delete()
        self.todo_list_blocks.pop(todo_list_name)

        self.order.remove(todo_list_name)

        self.update()

    def update_todo_list(self, todo_list_name, todos):
        self.todo_list_blocks[todo_list_name].set_todos(todos)

        self.update()

    def update_todo_list_name(self, old_name, new_name):
        # update todolist name only if old name exists
        if old_name in self.todo_list_blocks:
            self.todo_list_blocks.update({new_name: self.todo_list_blocks.pop(old_name)})
            self.todo_list_blocks[new_name].todo_list_title.set_text(new_name)
            self.todo_list_blocks[new_name].todo_list_name = new_name

            self.order = [key if key != old_name else new_name for key in self.order]

        self.update()

    # ---------------------------
    def todo_checked(self, todolist_name, todo):
        self.dispatch_message(403, ["CT", todolist_name, todo])

    def set_active_todo(self, ids):
        # set active todo_
        for key, block in self.todo_list_blocks.items():
            if (ids is not None and block.active_todo and key != ids[0]) or ids is None:
                block.active_todo_background.delete()
                block.active_todo_label.delete()
                block.active_todo = False

        try:
            if ids is not None:
                self.todo_list_blocks[ids[0]].set_active_todo(ids[1])

                # update order
                self.order.remove(ids[0])
                self.order.insert(0, ids[0])
        # Todo_list does no longer exist, just do not draw active sign
        except:
            pass

        # update
        self.update()

    # ---------------------------
    # draw/delete/update
    # ---------------------------
    def draw(self):
        self.draw_status = True
        # draw No todolist label
        if len(self.todo_list_blocks) == 0:
            self.no_todolist_label.draw()

        for _, block in self.todo_list_blocks.items():
            block.draw()

    def delete(self):
        self.draw_status = False
        # delete No todolist label
        self.no_todolist_label.delete()

        for _, block in self.todo_list_blocks.items():
            block.delete()

    def update(self):
        # check if y_scroll is still valid
        if self.corner_2[1] - self.corner_1[1] + self.y_scroll > self.height:
            self.y_scroll = scroll if (scroll := self.height - (self.corner_2[1] - self.corner_1[1])) > 0 else 0

        # update no todolist label pos
        if len(self.todo_list_blocks) == 0:
            self.no_todolist_label.set_center([self.corner_1[0], self.corner_1[1] - self.y_scroll])
        else:
            self.no_todolist_label.delete()

        # update block positions
        height = 0
        for name in self.order:
            self.todo_list_blocks[name].set_pos([self.corner_1[0], self.corner_1[1] + height - self.y_scroll], self.corner_2)
            height += self.todo_list_blocks[name].get_height()

        self.height = height

        if self.draw_status:
            self.draw()

    # ---------------------------
    # update positions
    # ---------------------------
    def set_pos(self, corner_1: [int, int], corner_2: [int, int]):
        self.corner_1 = corner_1
        self.corner_2 = corner_2

        self.update()

    def set_corner_1(self, corner_1: [int, int]):
        self.corner_1 = corner_1

        self.update()

    def set_corner_2(self, corner_2: [int, int]):
        self.corner_2 = corner_2

        self.update()

    # ---------------------------
    # window events
    # ---------------------------
    # left click
    def mouse_left_click(self, event):
        for block in self.todo_list_blocks.values():
            block.mouse_left_click(event)

    # right click
    def mouse_right_click(self, event):
        pass

    # mouse wheel
    def mouse_wheel(self, event):
        # scroll up
        if event.delta > 0 and self.y_scroll - 10 > 0:
            self.y_scroll -= 10
        elif event.delta > 0:
            self.y_scroll = 0
        # scroll down
        elif event.delta < 0 and self.corner_2[1] - self.corner_1[1] + self.y_scroll + 10 < self.height:
            self.y_scroll += 10
        elif event.delta < self.corner_2[1] - self.corner_1[1] + self.y_scroll < self.height:
            self.y_scroll = self.height - (self.corner_2[1] - self.corner_1[1])

        # end function if y_scroll did not change
        else:
            return None

        self.update()

# ----------------------------------------------------------------------------------------------------------------------
# todolist block
# ----------------------------------------------------------------------------------------------------------------------
class Todo_List_Block(object):
    def __init__(self, parent, root: tk.Tk, canvas: tk.Canvas, corner_1: [int, int], corner_2: [int, int], y_scroll: int,
                 text_color: [int, int, int], highlight_color: [int, int, int], todo_list_name, todos):
        self.parent = parent
        self.root = root
        self.canvas = canvas

        # todo_list arguments
        self.todo_list_name = todo_list_name
        self.todos = todos

        # position arguments
        self.corner_1 = corner_1
        self.corner_2 = corner_2
        self.y_scroll = y_scroll
        self.height = len(self.todos) * 25 + 110

        # colors
        self.text_color = text_color
        self.highlight_color = highlight_color

        # window elements
        self.draw_state = False
        self.todo_list_title = text.Text(self.canvas, self.todo_list_name, self.corner_1, [230, 230, 230], 20, anchor="nw")
        self.todo_blocks = []

        # active indicator
        self.active_todo = None
        self.active_todo_background = rectangle.Rectangle(self.canvas, [0, 0], [0, 0], 2, self.highlight_color, 0, self.highlight_color)
        self.active_todo_label = text.Text(self.canvas, "active", [0, 0], self.text_color, 10, anchor="nw")

        # add todo_elements
        self.add_todo_state = False
        x_pos, y_pos = self.corner_1[0] + 10, self.corner_1[1] + self.height - 60
        self.add_todo_label = text.Text(self.canvas, "new todo", [x_pos + 30, y_pos], [150, 150, 150], 15, anchor="nw")
        self.add_todo_line1 = line.Line(self.canvas, [x_pos, y_pos + 8], [x_pos + 13, y_pos + 8], [150, 150, 150], 1)
        self.add_todo_line2 = line.Line(self.canvas, [x_pos + 6, y_pos + 2], [x_pos + 6, y_pos + 15], [150, 150, 150], 1)

        self.update()

    def create_todo_elements(self):
        # delete elements
        while len(self.todos) < len(self.todo_blocks):
            self.todo_blocks[len(self.todos) - 1][0].delete()
            self.todo_blocks[len(self.todos) - 1][1].delete()

            self.todo_blocks.pop(len(self.todos) - 1)

        # create elements
        for i, todo in enumerate(self.todos):
            x_pos, y_pos = self.corner_1[0] + 10, self.corner_1[1] + 45 + (i * 25)

            # update existing components
            if len(self.todo_blocks) > i:
                self.todo_blocks[i][0].set_pos([x_pos, y_pos + 2], [x_pos + 10, y_pos + 12])
                self.todo_blocks[i][0].set_status(False)
                self.todo_blocks[i][1].set_corner_1([x_pos + 30, y_pos])
                self.todo_blocks[i][1].set_width(self.corner_2[0] - x_pos - 30)
                self.todo_blocks[i][1].set_text(todo[0])
            # create new components
            else:
                self.todo_blocks.append([
                    checkbox.Checkbox(self.canvas, [x_pos, y_pos + 2], [x_pos + 12, y_pos + 14], 0, self.highlight_color, 1, self.text_color),
                    entry.Entry(self.root, self.canvas, todo[0], [x_pos + 30, y_pos], self.corner_2[0] - x_pos - 30, [46, 51, 56], self.text_color, 15, bind=False)
                ])

            # create active indicator
            if self.active_todo == todo[3]:
                x_offset = self.todo_blocks[i][1].text.font.measure(self.todo_blocks[i][1].text.text) + 55

                self.active_todo_background.set_pos([x_pos + x_offset, y_pos + 2], [x_pos + x_offset + 36, y_pos + 14])
                self.active_todo_label.set_center([x_pos + x_offset + 5, y_pos + 2])

        self.height = len(self.todos) * 25 + 110

    # ---------------------------
    # update todos
    # ---------------------------
    def set_todos(self, todos):
        self.todos = todos

        # set active todo_at the top
        for i, todo in enumerate(self.todos):
            if todo[3] == self.active_todo:
                self.todos.insert(0, self.todos.pop(i))

        self.update()

        # update parent
        self.parent.update()

    def remove_todos(self, ids):
        for remove_todo in ids:
            self.todos = [todo for todo in self.todos if todo[3] != remove_todo]

        self.update()

        # update parent
        self.parent.update()

    def set_active_todo(self, id):
        self.active_todo = id

        # delete active todo_indicator if id is None
        if not self.active_todo:
            self.active_todo_background.delete()
            self.active_todo_label.delete()
        # put active todo_at the beginning of the list
        else:
            for i, todo in enumerate(self.todos):
                if todo[3] == self.active_todo:
                    self.todos.insert(0, self.todos.pop(i))

        # update
        self.update()

        # update parent
        self.parent.update()

    # ---------------------------
    # draw/delete/update
    # ---------------------------
    def draw(self):
        self.draw_state = True

        self.todo_list_title.draw()

        for block in self.todo_blocks:
            block[0].draw()
            block[1].draw()

        if self.active_todo:
            self.active_todo_background.draw()
            self.active_todo_label.draw()

        self.add_todo_label.draw()
        self.add_todo_line1.draw()
        self.add_todo_line2.draw()

    def delete(self):
        self.draw_state = False

        self.todo_list_title.delete()

        for block in self.todo_blocks:
            block[0].delete()
            block[1].delete()

        self.active_todo_background.delete()
        self.active_todo_label.delete()

        self.add_todo_label.delete()
        self.add_todo_line1.delete()
        self.add_todo_line2.delete()

    def update(self):
        # update elements
        self.todo_list_title.set_center(self.corner_1)

        self.create_todo_elements()

        x_pos, y_pos = self.corner_1[0] + 10, self.corner_1[1] + self.height - 60
        self.add_todo_label.set_center([x_pos + 30, y_pos])
        self.add_todo_line1.set_pos([x_pos, y_pos + 8], [x_pos + 13, y_pos + 8])
        self.add_todo_line2.set_pos([x_pos + 6, y_pos + 2], [x_pos + 6, y_pos + 15])

        # set entry as set if new todo_state is true
        if self.add_todo_state:
            self.todo_blocks[-1][1].enter_entry(self.corner_1[0])
            self.todo_blocks[-1][1].set_bind()
            self.todo_blocks[-1][1].bind_change = self.entry_update

        # draw elements
        if self.draw_state:
            self.draw()

    # ---------------------------
    # update/get positions
    # ---------------------------
    def set_pos(self, corner_1: [int, int], corner_2: [int, int]):
        self.corner_1 = corner_1
        self.corner_2 = corner_2

        self.update()

    def set_corner_1(self, corner_1: [int, int]):
        self.corner_1 = corner_1

        self.update()

    def set_corner_2(self, corner_2: [int, int]):
        self.corner_2 = corner_2

        self.update()

    def update_y_scroll(self, y_scroll):
        self.y_scroll = y_scroll

        self.update()

    def get_height(self):
        return self.height

    # ---------------------------
    # window events
    # ---------------------------
    # window resize
    def mouse_left_click(self, event):
        # checkbox press
        for i, block in enumerate(self.todo_blocks):
            if block[0].is_pressed(event.x, event.y):
                self.parent.todo_checked(self.todo_list_name, self.todos[i])

        # add new todo_pressed
        y_pos_1, y_pos_2 = self.corner_1[1] + self.height - 70, self.corner_1[1] + self.height - 35
        if self.corner_1[0] <= event.x <= self.corner_2[0] and y_pos_1 <= event.y <= y_pos_2:
            # set todolist state to add new todo_
            self.add_todo_state = True
            self.todos.append(["", None, None, None])

            # update
            self.update()
            self.parent.update()

    # entry update
    def entry_update(self, text):
        # dispatch message
        self.parent.dispatch_message(403, ["AT", self.todo_list_name, text])

        # update parameters
        self.todos[-1][0] = text
        self.todo_blocks[-1][1].unbind()
        self.add_todo_state = False