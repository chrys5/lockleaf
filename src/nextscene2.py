from asciimatics.exceptions import NextScene

class NextScene2(NextScene):
    def __init__(self, name, instance):
        super().__init__(name)
        instance["last_scene"] = {
            "Main Menu": 0,
            "Write Entry": 1,
            "Archives": 2,
            "Settings": 3,
            "Password": 4
        }[name]