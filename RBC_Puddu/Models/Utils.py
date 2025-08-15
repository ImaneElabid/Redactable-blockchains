from cryptography.fernet import Fernet
import json



if __name__ == '__main__':
    message = "hello world!"
    key = Fernet.generate_key()
    # Instance the Fernet class with the key
    message = json.dumps([], sort_keys=True)
    cipher = Fernet(key)
    encMessage = cipher.encrypt(message.encode())

    decMessage = cipher.decrypt(encMessage).decode()

    print("cipher: ", cipher)
    print("original string: ", message)
    print("encrypted string: ", encMessage)
    print("decrypted string: ", decMessage)