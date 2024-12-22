from asciimatics.screen import Screen
from asciimatics.scene import Scene
from asciimatics.event import KeyboardEvent
from asciimatics.exceptions import NextScene
from asciimatics.widgets import Frame, Layout, Text, Button, PopUpDialog

from entry_processes import save_entry
import sys

from nextscene2 import NextScene2

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
        self._ok_button = Button("OK", self._save_encrypted)
        self._cancel_button = Button("Cancel", self._return_to_write_entry)
        
        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(self._password_prompt)

        layout2 = Layout([50, 50])
        self.add_layout(layout2)
        layout2.add_widget(self._ok_button, 0)
        layout2.add_widget(self._cancel_button, 1)

        self.fix()

    def _save_encrypted(self):
        save_entry(self._instance["title"],
                    self._instance["folder"],
                    self._instance["entry"],
                    self._instance["media"],
                    self._instance["time_created"],
                    self._instance["root_path"],
                    self._password_prompt.value)
        self._instance["title"] = ""
        self._instance["title_readonly"] = False
        self._instance["folder"] = ""
        self._instance["entry"] = ""
        self._instance["media"] = []
        self._instance["time_created"] = ""
        self._password_prompt.value = ""
        raise NextScene2("Main Menu", self._instance)
    
    def _return_to_write_entry(self):
        raise NextScene2("Write Entry", self._instance)

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
                else:
                    self._password_prompt._hide_char = "*"
                self._password_prompt.update(0)
            
        return super().process_event(event)
