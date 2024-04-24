import json
import os

path = input("Enter root path: ")
while not os.path.isdir(path):
    path = input("Please enter a valid root path: ")

config_path = input("Enter path to config.json (permanent): ")
while not os.path.isdir(os.path.dirname(config_path)):
    config_path = input("Please enter a valid path to config.json (permanent): ")

with open(os.path.join(config_path, "config.json"), "w") as f:
    f.write(json.dump({"root_path": path, "theme": "default"}))

config_path = os.path.abspath(os.path.join(config_path, "config.json"))
with open(os.path.join(os.path.dirname(__file__), "consts.py"), "w") as f:
    f.write("CONFIG_PATH = " + config_path) 

print("Compiling to executable...")
os.system("pyinstaller --onefile lockleaf.py")

print("Done! Executable is in dist folder.")
