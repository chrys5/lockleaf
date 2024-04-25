import json
import os
import PyInstaller.__main__

path = input("Enter root path: ")
while not os.path.isdir(path):
    path = input("Please enter a valid root path: ")

config_path = os.path.join(os.path.dirname(__file__), "config")

with open(os.path.join(config_path, "config.json"), "w") as f:
    f.write(json.dump({"root_path": path, "theme": "default"}))

config_path = os.path.abspath(os.path.join(config_path, "config.json"))
with open(os.path.join(os.path.dirname(__file__), "consts.py"), "w") as f:
    f.write("CONFIG_PATH = " + config_path)

print("Compiling to executable...")
PyInstaller.__main__.run(["lockleaf.py", "--onefile", "--windowed"])

print("Done! Executable is in dist folder.")
