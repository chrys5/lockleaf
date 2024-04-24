from asciimatics.screen import Screen
from asciimatics.scene import Scene
from asciimatics.exceptions import NextScene, ResizeScreenError
from asciimatics.widgets import Frame, ListBox, Layout, Text, Button, Label, FileBrowser, Divider, TextBox, Widget, VerticalDivider, PopupMenu, PopUpDialog
from entry_processes import save_entry
import datetime

class Write_Entry(Frame):
    def __init__(self, screen, instance):
        super(Write_Entry, self).__init__(screen, 
                                        screen.height, 
                                        screen.width, 
                                        hover_focus=False,
                                        can_scroll=False)
        
        self._instance = instance
        self.set_theme(instance["theme"])
        self._title_box = Text(label="Title", name="Title")
        self._folder_box = Text(label="Folder", name="Folder")
        self._entry_box = TextBox(height=Widget.FILL_COLUMN, label="Entry", name="Entry", line_wrap=True, as_string=True)
        self._media = ListBox(height=Widget.FILL_COLUMN, options=[], label="Media", add_scroll_bar=True)
        # self._media_browser = FileBrowser(height=Widget.FILL_COLUMN, 
        #                                   root=ROOT_PATH, 
        #                                   name="Media", 
        #                                   on_select=self._select_media)
        
        self._save_popup = PopupMenu(screen=screen, 
                                     menu_items=[("Encrypt", self._prompt_password), 
                                                 ("Don't Encrypt", self._save_unencrypted),
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

    def _update_instance(self):
        self._instance["title"] = self._title_box.value
        self._instance["folder"] = self._folder_box.value
        self._instance["entry"] = self._entry_box.value
        self._instance["media"] = self._media.options

    def _save(self):
        self._update_instance()
        self.scene.add_effect(self._save_popup)

    def _prompt_password(self):
        raise NextScene("Password")
        
    def _save_unencrypted(self):
        save_entry(self._instance["title"],
                    self._instance["folder"],
                    self._instance["entry"],
                    self._instance["media"],
                    self._instance["time_created"],
                    self._instance["root_path"])
        self._leave(reset_instance=True)
        
    def _remove_popups(self):
        if self._save_popup in self.scene.effects:
            self.scene.remove_effect(self._save_popup)

    def _leave(self, reset_instance=False):
        raise ResizeScreenError("reset app 0")
        

    def _add_media(self):
        return
        self.scene.add_effect(FileBrowser(self._media, "/", name="Media", on_select=self._select_media))