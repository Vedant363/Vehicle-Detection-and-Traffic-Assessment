import gnupg
import getpass

# Initialize GPG instance
gpg = gnupg.GPG()

# Prompt user for passphrase
passphrase = getpass.getpass("Enter passphrase for encryption: ")

# Path to the file to be encrypted
input_file = "festive-utility-444415-f5-1d1bf70d3c99.json"
output_file = "credentials.json.gpg"

# Encrypt the file symmetrically
with open(input_file, "rb") as f:
    status = gpg.encrypt_file(
        f,
        recipients=None,
        output=output_file,
        symmetric=True,
        passphrase=passphrase
    )

# Check the result
if status.ok:
    print(f"File successfully encrypted: {output_file}")
else:
    print(f"Encryption failed: {status.status}")
