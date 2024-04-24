from asciimatics.screen import Screen
from asciimatics.scene import Scene
from asciimatics.effects import Print, Cycle
from asciimatics.particles import StarFirework, PalmFirework, SerpentFirework
from asciimatics.renderers import FigletText
from asciimatics.exceptions import NextScene, ResizeScreenError
from asciimatics.widgets import Frame, ListBox, Layout, Text, Button, Label, Divider, TextBox, Widget
import sys
import json

from screens.write_entry import Write_Entry
from screens.archives_screen import Archives
from screens.settings import Settings
from screens.password_screen import Password_Screen
from consts import CONFIG_PATH


instance = {}

class Main_Menu(Frame):
    def __init__(self, screen, instance):
        super(Main_Menu, self).__init__(screen, 
                                        screen.height, 
                                        screen.width,
                                        title="Lockleaf",
                                        hover_focus=True,
                                        can_scroll=False,
                                        reduce_cpu=True)
        
        self.set_theme(instance["theme"])
        self._list_view = ListBox(
            Widget.FILL_FRAME,
            [("Write Entry", 1), ("Archives", 2), ("Settings", 3), ("Exit", 4)],
            name="Main Menu",
            add_scroll_bar=True,
            on_select=self._select)
        
        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(self._list_view)

        self.fix()

    def _select(self):
        if self._list_view.value == 1:
            raise NextScene("Write Entry")
        elif self._list_view.value == 2:
            raise NextScene("Archives")
        elif self._list_view.value == 3:
            raise NextScene("Settings")
        elif self._list_view.value == 4:
            sys.exit(0)

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