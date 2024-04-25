import sys
import json
import os
import PyInstaller.__main__

path = input("Enter root path: ")
while not os.path.isdir(path):
    path = input("Please enter a valid root path: ")

config_path = os.path.join(os.path.dirname(__file__), "config")
if not os.path.isdir(config_path):
    os.mkdir(config_path)

with open(os.path.join(config_path, "config.json"), "w") as f:
    f.write(json.dumps({"root_path": path, "theme": "default"}))

config_path = os.path.abspath(os.path.join(config_path, "config.json"))
config_str = "CONFIG_PATH = \"" + config_path + "\""
config_str = config_str.replace("\\", "\\\\")
with open(os.path.join(os.path.join(os.path.dirname(__file__), "src"), "config.py"), "w") as f:
    f.write(config_str)

print("Compiling to executable...")
PyInstaller.__main__.run(["src/lockleaf.py", "--onefile", "--icon=52949.ico"])

print("Done! Executable is in dist folder.")
