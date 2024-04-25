from asciimatics.screen import Screen
from asciimatics.scene import Scene
from asciimatics.event import KeyboardEvent
from asciimatics.exceptions import NextScene
from asciimatics.widgets import Frame, Layout, Text, Button, PopUpDialog

from entry_processes import save_entry
import sys

class Password_Screen(Frame):
    def __init__(self, screen, instance):
        super(Password_Screen, self).__init__(screen, 
                                        screen.height, 
                                        screen.width, 
                                        hover_focus=False,
                                        can_scroll=False)
        
        self._instance = instance
        self.set_theme(instance["theme"])
        self._password_prompt = Text(label="Enter Password:", name="Password", hide_char="*")
        self._password_confirm = Text(label="Confirm Password:", name="Confirm Password", hide_char="*")
        self._ok_button = Button("OK", self._save_encrypted)
        self._cancel_button = Button("Cancel", self._return_to_write_entry)
        self._password_error = PopUpDialog(screen=screen, 
                                           text="Passwords do not match",
                                           buttons=["OK"])
        
        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(self._password_prompt)
        layout.add_widget(self._password_confirm)

        layout2 = Layout([50, 50])
        self.add_layout(layout2)
        layout2.add_widget(self._ok_button, 0)
        layout2.add_widget(self._cancel_button, 1)

        self.fix()

    def _save_encrypted(self):
        if self._password_prompt.value == self._password_confirm.value:
            save_entry(self._instance["title"],
                       self._instance["folder"],
                       self._instance["entry"],
                       self._instance["media"],
                       self._instance["time_created"],
                       self._instance["root_path"],
                       self._password_prompt.value)
            self._instance["title"] = ""
            self._instance["folder"] = ""
            self._instance["entry"] = ""
            self._instance["media"] = []
            self._instance["time_created"] = ""
            self._password_prompt.value = ""
            self._password_confirm.value = ""
            raise NextScene("Main Menu")
        else:
            self.scene.add_effect(self._password_error)
    
    def _return_to_write_entry(self):
        raise NextScene("Write Entry")

    def process_event(self, event):
        if isinstance(event, KeyboardEvent):
            if event.key_code == Screen.ctrl("q"):
                sys.exit(0)
            if event.key_code == Screen.KEY_ESCAPE:
                self._return_to_write_entry()
            if event.key_code == Screen.ctrl("h"):
                #toggle hide password
                if self._password_prompt._hide_char:
                    self._password_prompt._hide_char = None
                    self._password_confirm._hide_char = None
                else:
                    self._password_prompt._hide_char = "*"
                    self._password_confirm._hide_char = "*"
                self._password_prompt.update(0)
                self._password_confirm.update(0)
            
        return super().process_event(event)
