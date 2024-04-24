DEBUG = False

import os
import shutil
import json
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from gerbil.hash import hash

if DEBUG:
    import binascii

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BLOCK_SIZE = algorithms.AES.block_size
BUFFSIZE = BLOCK_SIZE * 1024 #128 byte buffer size
SALT_LENGTH = 24
IV_LENGTH = 16
HASH_LENGTH = 32
TAG_LENGTH = 16

def encrypt_file(file, password, delete=True, rename=None, isdir=False):
    """
    Encrypt a file or directory with a password.

    Parameters:
        file (str): The file or directory to be encrypted.
        password (str): The password to encrypt the file or directory with.
        delete (bool): Whether or not to delete the original file or directory.
        rename (str): The new name of the file or directory after decryption.

    Returns:
        str: The path to the encrypted file.
    """

    #get file name and extension
    dir = os.path.dirname(file)
    name = os.path.basename(file)

    #zip directory if necessary
    if not isdir and os.path.isdir(file):
        #zip the directory
        zipfile = shutil.make_archive(name, "zip", root_dir=os.path.join(dir, name))
        encrypted_file = encrypt_file(zipfile, password, delete=True, rename=name, isdir=True)
        if delete:
            secure_delete(file)
        return encrypted_file
    
    name, ext = os.path.splitext(name)

    #generate salt, initialization vector
    salt = os.urandom(24)
    initialization_vector = os.urandom(16)

    #generate key
    key_derivation_function = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = key_derivation_function.derive(password.encode())
    hashed_key = hash(key)

    #generate encryptor
    cipher = Cipher(
        algorithms.AES(key), 
        modes.GCM(initialization_vector), 
        backend=default_backend()
        )
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(BLOCK_SIZE).padder()

    #append metadata and metadata size to file
    metadata = {"name": name if rename == None else rename, "ext": ext, "isdir": isdir}
    metadata_str = json.dumps(metadata).encode()
    metadata_size = len(metadata_str)
    with open(file, 'ab') as infile:
        infile.write(metadata_str)
        infile.write(metadata_size.to_bytes(4, byteorder='big'))

    #encrypt file
    encrypted_file = os.path.join(dir, name + ".gerbil")
    with open(file, 'rb') as infile, open(encrypted_file, 'wb') as outfile:

        #write salt, initialization vector, hashed key, encryption tag space to outfile
        outfile.write(salt)
        outfile.write(initialization_vector)
        outfile.write(hashed_key)

        #write encrypted binary to outfile
        while True:
            data = infile.read(BUFFSIZE)

            #pad data if necessary
            if not len(data) % BLOCK_SIZE == 0:
                data = padder.update(data) + padder.finalize()

            encrypted_data = encryptor.update(data)
            outfile.write(encrypted_data)

            #finalize at last data buffer
            if len(data) < BUFFSIZE:
                outfile.write(encryptor.finalize())
                outfile.write(encryptor.tag)
                break
    
    #remove metadata from end of file
    with open(file, 'r+b') as infile:
            infile.seek(-4 - metadata_size, os.SEEK_END)
            infile.truncate()

    if delete:
        secure_delete(file)
    
    return encrypted_file


def decrypt_file(file, password, delete=True, rename=None):
    """
    Decrypt a file or directory with a password.

    Parameters:
        file (str): The file to be decrypted.
        password (str): The password to decrypt the file with.
        delete (bool): Whether or not to delete the encrypted file or directory.

    Returns:
        str: The path to the decrypted file.
        None: If the password is incorrect, the file is corrupted, or any other decryption error.
    """

    dir = os.path.dirname(file)
    name = os.path.basename(file)
    name, _ = os.path.splitext(name)

    with open(file, 'r+b') as infile:
        
        salt = infile.read(SALT_LENGTH)
        initialization_vector = infile.read(IV_LENGTH)
        hashed_key = infile.read(HASH_LENGTH)

        #verify password
        key_derivation_function = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = key_derivation_function.derive(password.encode())
        if not hash(key) == hashed_key:
            return None
        
        infile.seek(-TAG_LENGTH, os.SEEK_END)
        encryptor_tag = infile.read(TAG_LENGTH)
        infile.seek(-TAG_LENGTH, os.SEEK_END)
        infile.truncate()
        infile.seek(SALT_LENGTH + IV_LENGTH + HASH_LENGTH, os.SEEK_SET)
        
        #generate decryptor
        cipher = Cipher(
            algorithms.AES(key), 
            modes.GCM(initialization_vector), 
            backend=default_backend()
            )
        decryptor = cipher.decryptor()
        unpadder = padding.PKCS7(BLOCK_SIZE).unpadder()

        #decrypt file
        decrypted_file = os.path.join(dir, name + ".decrypting")
        decryption_failed = False
        with open(decrypted_file, 'wb') as outfile:
            while True:
                data = infile.read(BUFFSIZE)
                decrypted_data = decryptor.update(data)
                
                if len(data) < BUFFSIZE:
                    #unpad last data buffer
                    try:
                        decrypted_data += decryptor.finalize_with_tag(encryptor_tag)
                    except:
                        decryption_failed = True
                        break
                    decrypted_data = unpadder.update(decrypted_data) + unpadder.finalize()
                    outfile.write(decrypted_data)
                    break
                else:
                    outfile.write(decrypted_data)

        #reappend tag to end of file
        infile.seek(0, os.SEEK_END)
        infile.write(encryptor_tag)
    
        if decryption_failed:
            os.remove(decrypted_file)
            return None

    #get metadata from end of decrypted file and delete it
    with open(decrypted_file, 'r+b') as infile:
        infile.seek(-4, os.SEEK_END)
        metadata_size = int.from_bytes(infile.read(), byteorder='big')
        infile.seek(-4, os.SEEK_END)
        infile.truncate()
        infile.seek(-metadata_size, os.SEEK_END)
        metadata = json.loads(infile.read().decode())
        infile.seek(-metadata_size, os.SEEK_END)
        infile.truncate()
    
    name = metadata["name"] if rename == None else rename
    ext = metadata["ext"]
    isdir = metadata["isdir"]
    
    #rename decrypted file and unzip if necessary
    i = 0
    if isdir:
        decrypted_file_renamed = os.path.join(dir, name)
        while os.path.exists(decrypted_file_renamed):
            i += 1
            decrypted_file_renamed = os.path.join(dir, name + " (%d)" % (i))
        os.rename(decrypted_file, decrypted_file_renamed + ext)
        os.mkdir(decrypted_file_renamed)
        shutil.unpack_archive(decrypted_file_renamed + ext, extract_dir=decrypted_file_renamed)
        os.remove(decrypted_file_renamed + ext)
    else:
        decrypted_file_renamed = os.path.join(dir, name + ext)
        while os.path.exists(decrypted_file_renamed):
            i += 1
            decrypted_file_renamed = os.path.join(dir, name + " (%d)" % (i) + ext)
        os.rename(decrypted_file, decrypted_file_renamed)
    
    if delete:
        secure_delete(file)

    return decrypted_file_renamed
    
def secure_delete(file, passes=3):
    """
    Securely delete a file or directory.

    Parameters:
        file (str): The file or directory to be securely deleted.
    """

    if os.path.isdir(file):
        for root, dirs, files in os.walk(file):
            for name in files:
                secure_delete(os.path.join(root, name))
            for name in dirs:
                secure_delete(os.path.join(root, name))
        os.rmdir(file)
    else:
        with open(file, 'r+b') as infile:
            infile.seek(0, os.SEEK_END)
            file_size = infile.tell()
            for _ in range(passes):
                infile.seek(0, os.SEEK_SET)
                while infile.tell() < file_size:
                    infile.write(os.urandom(min(BUFFSIZE, file_size - infile.tell())))
                infile.flush()
                os.fsync(infile.fileno())
        os.remove(file)