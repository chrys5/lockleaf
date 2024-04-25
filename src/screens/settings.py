from asciimatics.screen import Screen
from asciimatics.scene import Scene
from asciimatics.event import KeyboardEvent
from asciimatics.particles import StarFirework, PalmFirework, SerpentFirework
from asciimatics.renderers import FigletText
from asciimatics.exceptions import NextScene, ResizeScreenError
from asciimatics.widgets import Frame, Layout, Text, Button, PopUpDialog, TextBox, Widget

import sys
import os
from config import CONFIG_PATH
from screens.write_entry import Write_Entry

class Settings(Frame):
    def __init__(self, screen, instance):
        super(Settings, self).__init__(screen, 
                                        screen.height, 
                                        screen.width, 
                                        hover_focus=False,
                                        can_scroll=True)

        self._instance = instance
        self.set_theme(instance["theme"])
        self._root_path = Text(label="Root Path", name="Root Path")
        self._theme = Text(label="Theme", name="Theme")
        self._ok_button = Button("OK", self._save_settings)
        self._back_button = Button("Back", self._cancel)

        self._about_text = TextBox(height=Widget.FILL_FRAME, as_string=True, line_wrap=True)

        self._pop_up = PopUpDialog(screen=screen,
                                    text="Invalid root path",
                                    buttons=["OK"])

        self._root_path.value = instance["root_path"]
        self._theme.value = instance["theme"]

        layout = Layout([100])
        self.add_layout(layout)
        layout.add_widget(self._root_path)
        layout.add_widget(self._theme)

        about = Layout([100], fill_frame=True)
        self.add_layout(about)
        about.add_widget(self._about_text)
        
        self._about_text.value =  """
Lockleaf is a simple journaling application that encrypts your entries. It is designed to be simple and easy to use and is perfect for those who want to keep their thoughts private. If you forget your password, you will not be able to recover your entries. Keep your password safe and secure.
Try not to resize the window, as it will cause the application to restart.

- Shortcuts:
    Ctrl + q: Exit
    Escape: Back
    Ctrl + h: Toggle show/hide password
- Main Menu Screen:
    Ctrl + w: Write Entry
    Ctrl + a: Archives 
- Write Entry Screen: 
    HOME: Go to beginning of line 
    END: Go to end of line
    PAGE UP: Go up one page
    PAGE DOWN: Go down one page
    DELETE: Delete line
    INSERT: Copy entry to clipboard
    Ctrl + e: Save entry with encryption (will prompt password)
    Ctrl + d: Save entry without encryption 
    Ctrl + m: Add media to entry (not working yet)
- Archives Screen: 
    Ctrl + w: Open selected entry 
    Ctrl + e: Encrypt all entries in folder 
    Ctrl + d: Decrypt all entries in folder 
    Ctrl + r: Go to root folder 
    DELETE: Delete entry or folder 
            """
        self._about_text._line = 0

        layout2 = Layout([50, 50])
        self.add_layout(layout2)
        layout2.add_widget(self._ok_button, 0)
        layout2.add_widget(self._back_button, 1)
        self.fix()

    def _save_settings(self):
        fix_backslashes = self._root_path.value.replace("\\", "\\\\")
        if not os.path.isdir(fix_backslashes):
            self.scene.add_effect(self._pop_up)
            return
        with open(CONFIG_PATH, "w") as f:
            f.write('{"root_path": "' + fix_backslashes + '", "theme": "' + self._theme.value + '"}')
        self._instance["root_path"] = self._root_path.value
        self._instance["theme"] = self._theme.value
        raise ResizeScreenError("refresh app 0")
    
    def _cancel(self):
        raise ResizeScreenError("refresh app 0")
    
    def process_event(self, event):
        if isinstance(event, KeyboardEvent):
            if event.key_code == Screen.ctrl("q"):
                sys.exit(0)
            elif event.key_code == Screen.KEY_ESCAPE:
                self._cancel()
        return super().process_event(event)