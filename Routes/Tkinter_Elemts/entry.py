import linecache
import tkinter as tk
from tkinter.font import Font

from Routes.Tkinter_Elemts import text, line

class Entry(object):
    def __init__(self, root: tk.Tk, canvas: tk.Canvas, entry_text: str, corner_1: [int, int], width: int,
                 background_color: [int, int, int], color: [int, int, int], font_size: int = 15,
                 font_family: str = "HarmonyOS Sans SC", placeholder: str = "Enter text", bind = True, text_fill_char = None):
        # assign variables
        self.root = root
        self.canvas = canvas

        self.corner_1 = corner_1
        self.width = width

        self.txt = entry_text
        self.text_fill_char = text_fill_char
        self.placeholder = placeholder

        self.bind_change = None

        # font information
        self.font_family = font_family
        self.font_size = font_size

        # create elements
        self.text = text.Text(canvas, entry_text, corner_1, color, font_size, font_family, tk.NW)
        self.entry = tk.Entry(root, bg=self.__rgb_to_hex(background_color), fg=self.__rgb_to_hex(color), bd=0, font=(font_family, -font_size))

        # bind ids
        self.canvas_bind_id = None
        self.entry_bind_id = None

        # replace text with text fill char if one is given
        if self.text_fill_char:
            entry_text = "".join([self.text_fill_char for _ in entry_text])

        # shorten new text to fit the boundaries
        if self.text.font.measure(entry_text) > self.width:
            for i in range(len(entry_text)):
                if self.text.font.measure(entry_text[:i + 1] + "...") > self.width:
                    entry_text = entry_text[:i] + "..."
                    break

        # check if entry was empty and set placeholder
        if len(entry_text) == 0:
            self.text.set_text(self.placeholder)
        # set text to final entry text
        else:
            self.text.set_text(entry_text)

        # bind events
        if bind:
            self.set_bind()

        # states
        self.edit = False
        self.drawn = False

    def set_bind(self):
        self.canvas_bind_id = self.canvas.bind("<Button-1>", self.is_pressed, add=True)
        self.entry_bind_id = self.entry.bind("<Return>", lambda event: self.leave_entry(), add=True)

    def unbind(self):
        if self.canvas_bind_id and self.entry_bind_id:
            self.canvas.unbind("<Button-1>", self.canvas_bind_id)
            self.entry.unbind("<Return>", self.entry_bind_id)

    def draw(self):
        self.drawn = True

        # draw text
        self.text.draw()

        if self.edit:
            # update entry content
            self.entry.delete(0 ,'end')
            self.entry.insert(0, self.txt)

            # place entry on screen
            self.entry.place(x=self.corner_1[0] - 3, y=self.corner_1[1] - 3, width=self.width)

    def delete(self):
        self.drawn = False

        self.text.delete()

        if self.edit:
            self.leave_entry()

    def leave_entry(self):
        if self.edit:
            self.edit = False

            # get the new text for the label
            new_text = self.entry.get()
            self.txt = new_text

            # replace text with text fill char if one is given
            if self.text_fill_char:
                new_text = "".join([self.text_fill_char for _ in new_text])

            # shorten new text to fit the boundaries
            if self.text.font.measure(new_text) > self.width:
                for i in range(len(new_text)):
                    if self.text.font.measure(new_text[:i + 1] + "...") > self.width:
                        new_text = new_text[:i] + "..."
                        break

            # check if entry was empty and set placeholder
            if len(new_text) == 0:
                self.text.set_text(self.placeholder)

            # set text to final entry text
            else:
                self.text.set_text(new_text)

            # destroy entry
            self.entry.place_forget()
            self.root.focus_set()

            # call bind function
            if self.bind_change is not None:
                self.bind_change(self.txt)

    def enter_entry(self, x):
        # turn to edit mode
        self.edit = True
        # update entry content
        self.entry.delete(0, 'end')
        self.entry.insert(0, self.txt)

        # place entry on screen and focus on it
        self.entry.place(x=self.corner_1[0] - 3, y=self.corner_1[1] - 3, width=self.width)

        # get cursor position
        last_dis = 0
        for i in range(len(self.txt)):
            if (click_offset := x - self.corner_1[0]) < (length := self.text.font.measure(self.txt[:i + 1])):
                # before
                if length - click_offset > last_dis:
                    self.entry.icursor(i)
                    break
                # after
                else:
                    self.entry.icursor(i + 1)
                    break

            last_dis = click_offset - length

        self.entry.focus_set()

    # update text parameter
    def set_text(self, text: str):
        # set variable
        self.txt = text

        # replace text with text fill char if one is given
        if self.text_fill_char:
            text = "".join([self.text_fill_char for _ in text])

        # shorten new text to fit the boundaries
        if self.text.font.measure(text) > self.width:
            for i in range(len(text)):
                if self.text.font.measure(text[:i + 1] + "...") > self.width:
                    text = text[:i] + "..."
                    break

        # check if entry was empty and set placeholder
        if len(text) == 0:
            self.text.set_text(self.placeholder)
        # set text
        else:
            self.text.set_text(text)

    def set_text_fill_char(self, char):
        self.text_fill_char = char

    # update placeholder parameter
    def set_placeholder(self, text: str):
        self.placeholder = text

    # update corner_1 parameter
    def set_corner_1(self, corner_1: [int, int]):
        self.corner_1 = corner_1

        self.text.set_center(corner_1)
        if self.edit:
            self.entry.place(x=self.corner_1[0] - 3, y=self.corner_1[1] - 3)

    # update width parameter
    def set_width(self, width: int):
        self.width = width

        self.set_text(self.txt)

    # update background color parameter
    def set_background_color(self, color: [int, int, int]):
        self.entry.configure(bg=self.__rgb_to_hex(color))

    # update color parameter
    def set_color(self, color: [int, int, int]):
        self.text.set_color(color)

        self.entry.configure(fg=self.__rgb_to_hex(color))

    # update font_size parameter
    def set_font_size(self, font_size: int):
        self.text.set_font_size(font_size)

    # update font_family parameter
    def set_font_family(self, font_family: str):
        self.text.set_font_family(font_family)

    # check if entry is pressed
    def is_pressed(self, event):
        # set click position
        x = event.x + self.corner_1[0] - 3 if self.root.focus_get() == self.entry else event.x
        y = event.y + self.corner_1[1] - 3 if self.root.focus_get() == self.entry else event.y

        # check if pressed
        if self.corner_1[0] <= x <= self.corner_1[0] + self.width and self.corner_1[1] <= y <= self.corner_1[1] + self.font_size and self.drawn:
            if not self.edit:
                self.enter_entry(x)

            return True

        # exit edit mode
        elif self.edit:
            self.leave_entry()

        return False

    @staticmethod
    def __rgb_to_hex(rgb):
        return "#{:02x}{:02x}{:02x}".format(round(rgb[0]), round(rgb[1]), round(rgb[2]))