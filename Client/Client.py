import socket
import rsa
import os
import hashlib
import base64
import json
import re

# Generate RSA key pair and save to files if not already present
def generate_or_load_keys():
    if not os.path.exists("client_public_key.pem") or not os.path.exists("client_private_key.pem"):
        print("RSA keys not found. Generating new keys...")
        (public_key, private_key) = rsa.newkeys(2048)

        with open("client_public_key.pem", "wb") as f:
            f.write(public_key.save_pkcs1())

        with open("client_private_key.pem", "wb") as f:
            f.write(private_key.save_pkcs1())

        print("New RSA keys generated and saved successfully.")
    else:
        print("RSA keys found. Using existing keys.")

    with open("client_public_key.pem", "rb") as f:
        public_key = rsa.PublicKey.load_pkcs1(f.read())
    with open("client_private_key.pem", "rb") as f:
        private_key = rsa.PrivateKey.load_pkcs1(f.read())

    return public_key, private_key

# Register the client with a username
def register_client():
    username = input("Enter your username: ")

    username = re.sub(r'[^\w\s]', '_', username).strip()

    print(f"Registered username: {username}")
    return username

# Select a public key for encryption
def select_public_key_for_encryption():
    while True:
        key_path = input("Enter the path to the receiver's public key file for encryption: ")
        try:
            with open(key_path, "rb") as f:
                public_key = rsa.PublicKey.load_pkcs1(f.read())
            print(f"Successfully loaded public key from {key_path}.")
            return public_key
        except Exception as e:
            print(f"Error loading public key: {e}. Please try again.")

# Encrypt the message using the RSA public key
def encrypt_message(message, public_key):
    try:
        encrypted_message = rsa.encrypt(message.encode('utf-8'), public_key)
        return encrypted_message
    except Exception as e:
        print(f"Error encrypting the message: {e}")
        return None

# Decrypt the message using the RSA private key
def decrypt_message(encrypted_message, private_key):
    try:
        decrypted_message = rsa.decrypt(base64.b64decode(encrypted_message), private_key).decode('utf-8')
        return decrypted_message
    except Exception as e:
        print(f"Error decrypting the message: {e}")
        return None

# Communicate with the server
def client_communication(server_host, server_port):
    username = register_client()
    public_key, private_key = generate_or_load_keys()

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_host, server_port))
        print(f"Connected to server {server_host}:{server_port}")

        client_socket.send(public_key.save_pkcs1())  # Send the public key
        client_socket.send(username.encode('utf-8'))  # Send the username

        while True:
            action = input("Choose an action: 1) Send Message 2) Retrieve Messages 3) Exit: ").strip()
            if action == '1':
                client_socket.send(b'send_message')
                receiver_public_key = select_public_key_for_encryption()
                message = input("Enter the message to send: ")

                encrypted_message = encrypt_message(message, receiver_public_key)
                if encrypted_message:
                    client_socket.send(receiver_public_key.save_pkcs1())  # Send receiver's public key
                    client_socket.send(encrypted_message)  # Send encrypted message
                    print("Encrypted message sent successfully.")
                else:
                    print("Message encryption failed.")

                response = client_socket.recv(4096).decode('utf-8')
                print(f"Server response: {response}")

            elif action == '2':
                client_socket.send(b'retrieve_messages')
                response = client_socket.recv(4096)  # Receive server's response

                try:
                    messages = json.loads(response.decode('utf-8'))  # Try to decode the response as JSON
                    if not messages:
                        print("No messages found.")
                    else:
                        for msg in messages:
                            encrypted_msg = msg["encrypted_message"]
                            decrypted_msg = decrypt_message(encrypted_msg, private_key)
                            print(f"From: {msg['sender_public_key']}\nMessage: {decrypted_msg}\n")
                except json.JSONDecodeError:
                    print("Error: Received invalid JSON response from the server.")
                    print(f"Server response: {response.decode('utf-8')}")

            elif action == '3':
                print("Exiting...")
                break

            else:
                print("Invalid choice. Please try again.")

        client_socket.close()

    except Exception as e:
        print(f"Error connecting to the server: {e}")

# Ensure the correct entry point
if __name__== "__main__":
    server_host = "172.25.208.58"  # Updated IP address
    server_port = 12345
    client_communication(server_host, server_port)