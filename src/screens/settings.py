from asciimatics.screen import Screen
from asciimatics.scene import Scene
from asciimatics.effects import Print, Cycle
from asciimatics.particles import StarFirework, PalmFirework, SerpentFirework
from asciimatics.renderers import FigletText
from asciimatics.exceptions import NextScene, ResizeScreenError
from asciimatics.widgets import Frame, Layout, Text, Button, PopUpDialog, TextBox, Widget

import os
from consts import CONFIG_PATH
from screens.write_entry import Write_Entry

class Settings(Frame):
    def __init__(self, screen, instance):
        super(Settings, self).__init__(screen, 
                                        screen.height, 
                                        screen.width, 
                                        hover_focus=False,
                                        can_scroll=False)

        self._instance = instance
        self.set_theme(instance["theme"])
        self._root_path = Text(label="Root Path", name="Root Path")
        self._theme = Text(label="Theme", name="Theme")
        self._ok_button = Button("OK", self._save_settings)
        self._back_button = Button("Back", self._cancel)

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
        about.add_widget(TextBox(Widget.FILL_FRAME, "Lockleaf is a simple journaling application that encrypts your entries. It is designed to be simple and easy to use and is perfect for those who want to keep their thoughts private.", readonly=True))

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
        raise NextScene("Main Menu")