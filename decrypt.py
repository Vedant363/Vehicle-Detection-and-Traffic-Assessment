import gnupg
import getpass

# Initialize GPG instance
gpg = gnupg.GPG()

# Prompt user for passphrase
passphrase = getpass.getpass("Enter passphrase for decryption: ")

# Path to the encrypted file
input_file = "credentials.json.gpg"
output_file = "credentials.json"

# Decrypt the file symmetrically
with open(input_file, "rb") as f:
    status = gpg.decrypt_file(
        f,
        output=output_file,
        passphrase=passphrase
    )

# Check the result
if status.ok:
    print(f"File successfully decrypted: {output_file}")
else:
    print(f"Decryption failed: {status.status}")
