# decrypt_file.py
import gnupg
import getpass
import os
import atexit
import signal
from models.state import DecryptionStatus 

gpg = gnupg.GPG()
input_file = "credentials.json.gpg"
output_file = "credentials.json"

def _cleanup():
    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"Deleted decrypted file: {output_file}")

atexit.register(_cleanup)

def _handle_exit_signals(signum, frame):
    print(f"Received termination signal ({signum}). Cleaning up...")
    _cleanup()
    exit(0)

signal.signal(signal.SIGINT, _handle_exit_signals)
signal.signal(signal.SIGTERM, _handle_exit_signals)

def decrypt_file():
    passphrase = getpass.getpass("Enter passphrase for decryption: ")

    with open(input_file, "rb") as f:
        status = gpg.decrypt_file(f, output=output_file, passphrase=passphrase)

    if status.ok:
        DecryptionStatus.set_decryption_status(True)  
        print(f"File successfully decrypted: {output_file}")
    else:
        print(f"Decryption failed: {status.status}")
        exit(1)

def check_decryption_status():
    return DecryptionStatus.get_decryption_status()  

if __name__ == "__main__":
    decrypt_file()
