import re
import os
import json
from gerbil.encryption import encrypt_file, decrypt_file

def is_encrypted(entry_path):
    return entry_path.endswith("[ENCRYPTED].lockleaf")

def save_entry(title, folder, entry, media, time_created, root_path, password=None):
        #check folder value and create folder if it doesn't exist
        path_to_entry = re.split(r'[\/\\]', folder)
        path = root_path
        for f in path_to_entry:
            path = os.path.join(path, f)
            if not os.path.isdir(path):
                os.mkdir(path)
        if not os.path.isdir(os.path.join(path, "0")):
            os.mkdir(os.path.join(path, "0"))
        
        file_name = time_created + " - " + title + ".lockleaf"
        #remove invalid characters from file name
        file_name = re.sub(r'[\\/:*?"<>|]', "", file_name)
        entry_path = os.path.join(path, file_name)

        #write entry to txt file
        with open(entry_path, "w") as f:
            f.write(json.dumps({"title": title, 
                                "folder": folder, 
                                "entry": entry, 
                                "media": media,
                                "time_created": time_created}))
        #encrypt if password is not None
        if password is not None:
            encrypt_entry(entry_path, password)

def load_entry(entry_path, password=None):
    if password is None:
        password = ""
    if is_encrypted(entry_path):
        entry_path = decrypt_file(entry_path, password)
    if entry_path is None:
        return None
    with open(entry_path, "r") as f:
        entry = json.load(f)
    return entry

def encrypt_entry(entry_path, password):
    path = os.path.dirname(entry_path)
    time_created = re.split(r'\s-\s', os.path.basename(entry_path))[0]
    os.rename(encrypt_file(entry_path, password), 
              os.path.join(path, time_created + " - [ENCRYPTED]" + ".lockleaf"))
    
def decrypt_entry(entry_path, password):
    return decrypt_file(entry_path, password)   