from asciimatics.screen import Screen
from asciimatics.scene import Scene
from asciimatics.event import KeyboardEvent
from asciimatics.exceptions import NextScene, ResizeScreenError
from asciimatics.effects import Print, Cycle, Stars, Wipe, BannerText, Mirage, Matrix, Clock, RandomNoise, Scroll, Cog, Print
from asciimatics.widgets import Frame, Label, Layout, Text, Button, VerticalDivider, Divider, TextBox, Widget, PopupMenu, Widget
import sys
import json

from screens.write_entry import Write_Entry
from screens.archives_screen import Archives
from screens.settings import Settings
from screens.password_screen import Password_Screen
from config import CONFIG_PATH

import numpy.random as random

instance = {}

class Main_Menu(Frame):
    def __init__(self, screen, instance):
        super(Main_Menu, self).__init__(screen,
                                        screen.height,
                                        screen.width,
                                        title="Lockleaf",
                                        hover_focus=False,
                                        can_scroll=False,
                                        reduce_cpu=True)
        
        self.set_theme(instance["theme"])

        art = Layout([1], fill_frame=True)
        self.add_layout(art)
        #generate dust field effect of screen height and width
        for _ in range(screen.height):
            art.add_widget(Label("".join(random.choice([" ", "*", "+", "@", "."], screen.width-2, p=[0.94, 0.02, 0.01, 0.0005, 0.0295]))))

        self._write_entry_button = Button("< Write Entry >", self._write_entry, add_box=False)
        self._archives_button = Button("< Archives >", self._archives, add_box=False)
        self._settings_button = Button("< Settings >", self._settings, add_box=False)
        self._exit_button = Button("< Exit >", self._exit, add_box=False)

        while len(self._write_entry_button.text) < screen.width//4-1:
            self._write_entry_button.text = " " + self._write_entry_button.text + " "
        while len(self._archives_button.text) < screen.width//4-1:
            self._archives_button.text = " " + self._archives_button.text + " "
        while len(self._settings_button.text) < screen.width//4-1:
            self._settings_button.text = " " + self._settings_button.text + " "
        while len(self._exit_button.text) < screen.width//4-1:
            self._exit_button.text = " " + self._exit_button.text + " "

        div = Layout([1])
        self.add_layout(div)
        div.add_widget(Divider())

        layout = Layout([1, 1, 1, 1])
        self.add_layout(layout)
        layout.add_widget(self._write_entry_button, 0)
        layout.add_widget(self._archives_button, 1)
        layout.add_widget(self._settings_button, 2)
        layout.add_widget(self._exit_button, 3)


        self.fix()

    def _write_entry(self): raise NextScene("Write Entry")

    def _archives(self): raise NextScene("Archives")
    
    def _settings(self): raise NextScene("Settings")
        
    def _exit(self): sys.exit(0)

    def process_event(self, event):
        if isinstance(event, KeyboardEvent):
            if event.key_code == Screen.ctrl("q"):
                sys.exit(0)
            if event.key_code == Screen.ctrl("w"):
                raise NextScene("Write Entry")
            if event.key_code == Screen.ctrl("a"):
                raise NextScene("Archives")
        return super().process_event(event)

def demo(screen, sceneidx, instance):
    #parse config file
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)

    scenes = []
    if instance == {}: #first time running
        instance = {
                    "title": "",
                    "title_readonly": False,
                    "folder": "",
                    "entry": "",
                    "media": [],
                    "time_created": "",
                    "root_path": config["root_path"],
                    "theme": config["theme"],
                    "scenes": scenes,
                }

    scenes_list = [
        Scene([Main_Menu(screen, instance)], -1, name = "Main Menu"),
        Scene([Write_Entry(screen, instance)], -1, name = "Write Entry"),
        Scene([Archives(screen, instance)], -1, name = "Archives"),
        Scene([Settings(screen, instance)], -1, name = "Settings"),
        Scene([Password_Screen(screen, instance)], -1, name = "Password"),
    ]
    for s in scenes_list:
        scenes.append(s)

    screen.play(scenes, stop_on_resize=True, start_scene=scenes_list[sceneidx])

def start():
    last_scene = 0
    while True:
        try:
            Screen.wrapper(demo, catch_interrupt=True, arguments=[last_scene, instance])
        except ResizeScreenError as e:
            if e.__str__()[-1] == '2':
                last_scene = 2
            else:
                last_scene = 0