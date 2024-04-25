from asciimatics.screen import Screen
from asciimatics.scene import Scene
from asciimatics.event import KeyboardEvent
from asciimatics.exceptions import NextScene, ResizeScreenError
from asciimatics.widgets import Frame, PopUpDialog, Layout, FileBrowser, Widget, Text, Button

from gerbil.encryption import secure_delete
from entry_processes import encrypt_entry, decrypt_entry, load_entry, is_encrypted

import sys
import os

class Archives(Frame):
    def __init__(self, screen, instance):
        super(Archives, self).__init__(screen, 
                                        screen.height, 
                                        screen.width, 
                                        hover_focus=False,
                                        can_scroll=False)
        

        self._instance = instance
        self.set_theme(instance["theme"])
        root_path = self._instance["root_path"]
        self._file_browser = FileBrowser(height=Widget.FILL_COLUMN, 
                                     root=root_path, 
                                     name="FileBrowser",
                                     on_select=self._open_entry,
                                     on_change=self._update_buttons,
                                     file_filter=".*.lockleaf")
        self._selected_file = Text(label="Selected File:", name="Selected File", readonly=True)
        self._selected_file.disabled = True
        self._password_prompt = Text(label="Password:", name="Password", hide_char="*")
        
        self._back_to_root_button = Button("Root", self._back_to_root)
        self._encrypt_folder_button = Button("Encrypt All Entries", self._encrypt_folder)
        self._decrypt_folder_button = Button("Decrypt All Entries", self._decrypt_folder)
        self._open_button = Button("Open", self._open_entry)
        self._delete_button = Button("Delete", self._delete)
        self._back_button = Button("Back", self._cancel)
        
        self._invalid_password = PopUpDialog(screen=screen,
                                                text="Invalid Password",
                                                buttons=["OK"])
        self._delete_confirm = PopUpDialog(screen=screen,
                                            text="You sure?",
                                            buttons=["No", "Yes"],
                                            on_close=self._delete_confirm_action)
        
        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(self._file_browser)

        text_layout = Layout([100])
        self.add_layout(text_layout)
        text_layout.add_widget(self._selected_file)
        text_layout.add_widget(self._password_prompt)

        layout2 = Layout([2, 2, 1, 1, 1, 1])
        self.add_layout(layout2)
        
        layout2.add_widget(self._encrypt_folder_button, 0)
        layout2.add_widget(self._decrypt_folder_button, 1)
        layout2.add_widget(self._back_to_root_button, 2)
        layout2.add_widget(self._open_button, 3)
        layout2.add_widget(self._delete_button, 4)
        layout2.add_widget(self._back_button, 5)

        self.fix()

    def _update_buttons(self):
        self._selected_file.value = self._file_browser.value
        if os.path.isdir(self._file_browser.value):
            self._encrypt_folder_button.disabled = False
            self._decrypt_folder_button.disabled = False
            self._open_button.disabled = True
            if self._file_browser.value == self._instance["root_path"] or not self._file_browser.value.startswith(self._instance["root_path"]):
                self._password_prompt.disabled = True
                self._delete_button.disabled = True
            elif os.path.basename(self._selected_file.value) == "0":
                self._password_prompt.disabled = False
                self._delete_button.disabled = True
            else:
                self._password_prompt.disabled = False
                self._delete_button.disabled = False
        else:
            self._encrypt_folder_button.disabled = True
            self._decrypt_folder_button.disabled = True
            self._open_button.disabled = False
            self._delete_button.disabled = False
            if is_encrypted(self._file_browser.value):
                self._password_prompt.disabled = False
            else:
                self._password_prompt.disabled = True

    def _encrypt_folder(self):
        folder_path = self._file_browser.value
        if os.path.basename(folder_path) == "0":
            folder_path = os.path.dirname(folder_path)
        password = self._password_prompt.value
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if not is_encrypted(file):
                    encrypt_entry(os.path.join(root, file), password)
        self.screen.refresh()
        self._password_prompt.value = ""
        raise ResizeScreenError("refresh app 2")

    def _decrypt_folder(self):
        folder_path = self._file_browser.value
        if os.path.basename(folder_path) == "0":
            folder_path = os.path.dirname(folder_path)
        password = self._password_prompt.value

        invalid_password = False
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if is_encrypted(file):
                    if decrypt_entry(os.path.join(root, file), password) == None:
                        invalid_password = True
        self.screen.refresh()
        if invalid_password:
            self.scene.add_effect(self._invalid_password)
        else:
            self._password_prompt.value = ""
            raise ResizeScreenError("refresh app 2")

    def _open_entry(self):
        entry_path = self._file_browser.value
        password = self._password_prompt.value
        entry = load_entry(entry_path, password)
        if entry is None:
            self.scene.add_effect(self._invalid_password)
            return
        self._instance["title"] = entry["title"]
        self._instance["folder"] = entry["folder"]
        self._instance["entry"] = entry["entry"]
        self._instance["media"] = entry["media"]
        self._instance["time_created"] = entry["time_created"]
        self._instance["title_readonly"] = True
        self._password_prompt.value = ""
        raise NextScene("Write Entry")

    def _delete(self):
        self.scene.add_effect(self._delete_confirm)

    def _delete_confirm_action(self, selected):
        if selected == 1:
            entry_path = self._file_browser.value
            secure_delete(entry_path)
            #go to parent directory and back to refresh file browser
            self._file_browser.value = os.path.dirname(entry_path)
            self._file_browser.value = os.path.dirname(self._file_browser.value)
            raise ResizeScreenError("refresh app 2")

    def _back_to_root(self):
        raise ResizeScreenError("refresh app 2")

    def _cancel(self):
        self._password_prompt.value = ""
        raise NextScene("Main Menu")
    
    def process_event(self, event):
        if isinstance(event, KeyboardEvent):
            if event.key_code == Screen.ctrl("q"):
                sys.exit(0)
            elif event.key_code == Screen.KEY_ESCAPE:
                self._cancel()
            if event.key_code == Screen.ctrl("h"):
                #toggle hide password
                if self._password_prompt._hide_char:
                    self._password_prompt._hide_char = None
                else:
                    self._password_prompt._hide_char = "*"
                self._password_prompt.update(0)
            elif event.key_code == Screen.ctrl("w"):
                if self._open_button.disabled == False:
                    self._open_entry()
            elif event.key_code == Screen.ctrl("r"):
                self._back_to_root()
            elif event.key_code == Screen.ctrl("e"):
                if self._encrypt_folder_button.disabled == False:
                    self._encrypt_folder()
            elif event.key_code == Screen.ctrl("d"):
                if self._decrypt_folder_button.disabled == False:
                    self._decrypt_folder()
            elif event.key_code == Screen.KEY_DELETE:
                if self._delete_button.disabled == False:
                    self._delete()
            else:
                pass
        return super().process_event(event)