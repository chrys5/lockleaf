from asciimatics.screen import Screen
from asciimatics.scene import Scene
from asciimatics.event import KeyboardEvent
from asciimatics.exceptions import ResizeScreenError
from asciimatics.widgets import Frame, ListBox, Layout, Text, Button, Label, FileBrowser, Divider, TextBox, Widget, VerticalDivider, PopupMenu, PopUpDialog
from entry_processes import save_entry
import sys
import pyperclip
import datetime

from nextscene2 import NextScene2

class Write_Entry(Frame):
    def __init__(self, screen, instance):
        super(Write_Entry, self).__init__(screen, 
                                        screen.height, 
                                        screen.width, 
                                        on_load=self.load_instance,
                                        hover_focus=False,
                                        can_scroll=True)
        
        self._instance = instance
        self.set_theme(instance["theme"])
        self._title_box = Text(label="Title", name="Title", on_change=self._update_title_in_instance)
        self._folder_box = Text(label="Folder", name="Folder", on_change=self._update_folder_in_instance)
        self._entry_box = TextBox(height=Widget.FILL_COLUMN, label="Entry", name="Entry", line_wrap=True, as_string=True, on_change=self._update_entry_in_instance)

        self._media = ListBox(height=Widget.FILL_COLUMN, options=[], label="Media", add_scroll_bar=True)
        # self._media_browser = FileBrowser(height=Widget.FILL_COLUMN, 
        #                                   root=ROOT_PATH, 
        #                                   name="Media", 
        #                                   on_select=self._select_media)
        
        self._save_popup = PopupMenu(screen=screen, 
                                     menu_items=[("Encrypt", self._prompt_password), 
                                                 ("Save", self._save_unencrypted),
                                                 ("Cancel", self._remove_popups)], 
                                    x=2, 
                                    y=screen.height-3)
        self._save_popup.set_theme(instance["theme"])

        self.load_instance(update_time_display = False)
        if self._instance["time_created"] == "":
            self._instance["time_created"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._time_display = Label(self._instance["time_created"], align=">")

        layout = Layout([70, 2, 30])
        self.add_layout(layout)
        layout.add_widget(self._title_box, 0)
        layout.add_widget(VerticalDivider(), 1)
        layout.add_widget(self._folder_box, 2)
        layout.add_widget(Divider(), 0)
        layout.add_widget(Divider(), 1)
        layout.add_widget(Divider(), 2)

        layout2 = Layout([100, 2, 20], fill_frame=True)
        self.add_layout(layout2)
        layout2.add_widget(self._entry_box, 0)
        layout2.add_widget(VerticalDivider(), 1)
        layout2.add_widget(self._time_display, 2)
        layout2.add_widget(Divider(), 2)
        layout2.add_widget(self._media, 2)
        
        layout3 = Layout([51, 51, 20])
        self.add_layout(layout3)
        layout3.add_widget(Button("Save", self._save), 0)
        layout3.add_widget(Button("Back", self._leave), 1)
        layout3.add_widget(Button("Add Media", self._add_media, disabled=True), 2)
        self._media.disabled = True

        self.fix()
    
    def load_instance(self, update_time_display=True):
        self._title_box.value = self._instance["title"]
        self._title_box.readonly = self._instance["title_readonly"]
        self._folder_box.readonly = self._instance["title_readonly"]
        self._folder_box.value = self._instance["folder"]
        self._entry_box.value = self._instance["entry"]
        self._media.options = self._instance["media"]
        if update_time_display:
            self._time_display.text = self._instance["time_created"]

    def _update_title_in_instance(self):
        self._instance["title"] = self._title_box.value
    
    def _update_folder_in_instance(self):
        self._instance["folder"] = self._folder_box.value
    
    def _update_entry_in_instance(self):
        self._instance["entry"] = self._entry_box.value

    def _update_instance(self):
        self._instance["title"] = self._title_box.value
        self._instance["folder"] = self._folder_box.value
        self._instance["entry"] = self._entry_box.value
        self._instance["media"] = self._media.options

    def _save(self):
        self.scene.add_effect(self._save_popup)

    def _prompt_password(self):
        self._update_instance()
        raise NextScene2("Password", self._instance)
        
    def _save_unencrypted(self):
        self._update_instance()
        save_entry(self._instance["title"],
                    self._instance["folder"],
                    self._instance["entry"],
                    self._instance["media"],
                    self._instance["time_created"],
                    self._instance["root_path"])
        
    def _remove_popups(self):
        if self._save_popup in self.scene.effects:
            self.scene.remove_effect(self._save_popup)

    def _leave(self, reset_instance=True):
        if reset_instance:
            self._instance["title"] = ""
            self._instance["title_readonly"] = False
            self._instance["folder"] = ""
            self._instance["entry"] = ""
            self._instance["media"] = []
            self._instance["time_created"] = ""
        raise NextScene2("Main Menu", self._instance)
        
    def process_event(self, event):
        if isinstance(event, KeyboardEvent):
            if event.key_code == Screen.ctrl("q"):
                sys.exit(0)
            elif event.key_code == Screen.KEY_ESCAPE:
                self._leave()
            elif event.key_code == Screen.ctrl("d"):
                self._save_unencrypted()
            elif event.key_code == Screen.ctrl("e"):
                self._prompt_password()
            elif event.key_code == Screen.ctrl("m"):
                self._add_media()
            elif event.key_code == Screen.KEY_DELETE:
                if not self._entry_box.value:
                    return
                curr_line = self._entry_box._line
                line_arr = self._entry_box.value.split("\n")
                if curr_line < len(line_arr):
                    line_arr.pop(curr_line)
                    self._entry_box.value = "\n".join(line_arr)
                    self._entry_box._line = curr_line
                    if curr_line == len(line_arr) and curr_line > 0:
                        self._entry_box._line -= 1
            elif event.key_code == Screen.KEY_INSERT:
                #copy entry to clipboard
                pyperclip.copy(self._entry_box.value)
            else:
                pass
        return super().process_event(event)

    def _add_media(self):
        return
        self.scene.add_effect(FileBrowser(self._media, "/", name="Media", on_select=self._select_media))