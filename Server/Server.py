import hashlib
import time
import socket
import threading
import json
import base64
from filelock import FileLock  # Requires pip install filelock

MEMBERS_FILE = "members.txt"
BLOCKCHAIN_FILE = "blockchain.json"

def calculate_hash(index, previous_hash, timestamp, data):
    """Calculates the hash of a block."""
    value = str(index) + str(previous_hash) + str(timestamp) + str(data)
    return hashlib.sha256(value.encode()).hexdigest()

def create_new_block(previous_index, previous_hash, data):
    """Creates a new block and appends it to the blockchain."""
    index = previous_index + 1
    timestamp = int(time.time())
    hash = calculate_hash(index, previous_hash, timestamp, data)

    lock = FileLock(f"{BLOCKCHAIN_FILE}.lock")
    with lock, open(BLOCKCHAIN_FILE, "a+") as f:
        f.seek(0, 2)  # Seek to the end of the file
        new_block = {
            "index": index,
            "previous_hash": previous_hash,
            "timestamp": timestamp,
            "data": data,
            "hash": hash,
        }
        json.dump(new_block, f)
        f.write("\n")

    return index, hash

def load_last_block():
    """Loads the last block from the blockchain file."""
    try:
        with open(BLOCKCHAIN_FILE, "r") as f:
            lines = f.readlines()
            if lines:
                last_block = json.loads(lines[-1].strip())
                return last_block["index"], last_block["hash"]
            else:
                return initialize_blockchain()
    except FileNotFoundError:
        return initialize_blockchain()

def initialize_blockchain():
    """Creates the genesis block."""
    timestamp = int(time.time())
    index = 0
    previous_hash = "0"
    data = "Genesis Block"
    hash = calculate_hash(index, previous_hash, timestamp, data)

    with open(BLOCKCHAIN_FILE, "w") as f:
        genesis_block = {
            "index": index,
            "previous_hash": previous_hash,
            "timestamp": timestamp,
            "data": data,
            "hash": hash,
        }
        json.dump(genesis_block, f)
        f.write("\n")

    return index, hash

def encode_public_key(public_key_bytes):
    """Encodes the public key to Base64."""
    return base64.b64encode(public_key_bytes).decode('utf-8')

def store_member(username, public_key):
    """Store the member's username and public key in members.txt."""
    try:
        with open(MEMBERS_FILE, "r") as f:
            members = f.readlines()
    except FileNotFoundError:
        members = []

    encoded_public_key = encode_public_key(public_key)

    for member in members:
        if not member.strip():
            continue
        try:
            existing_username, existing_public_key = member.strip().split(", ")
            if existing_username == username and existing_public_key == encoded_public_key:
                return
        except ValueError:
            continue

    with open(MEMBERS_FILE, "a") as f:
        f.write(f"{username}, {encoded_public_key}\n")

def retrieve_messages(public_key):
    """Retrieves all messages for the given public key."""
    try:
        with open(BLOCKCHAIN_FILE, "r") as f:
            blocks = [json.loads(line.strip()) for line in f.readlines()]

        messages = []
        for block in blocks[1:]:
            data = block.get("data", {})
            if data.get("receiver_public_key") == public_key:
                messages.append(data)
        return messages
    except Exception as e:
        print(f"Error retrieving messages: {e}")
        return []

def handle_client(client_socket, client_address, blockchain_state):
    """Handles client connections and messages."""
    try:
        # Receive sender's public key and username
        sender_public_key_bytes = client_socket.recv(2048)
        username = client_socket.recv(1024).decode('utf-8', errors='replace')

        # Store the member if not already stored
        store_member(username, sender_public_key_bytes)

        # Receive the action type ('send_message' or 'retrieve_messages')
        action = client_socket.recv(1024).decode('utf-8')

        if action == 'send_message':
            # Receive receiver's public key and the encrypted message
            receiver_public_key_bytes = client_socket.recv(2048)
            encrypted_message = client_socket.recv(2048)

            # Store the new message in the blockchain
            previous_index, previous_hash = blockchain_state
            blockchain_state[:] = create_new_block(previous_index, previous_hash, {
                "sender_public_key": base64.b64encode(sender_public_key_bytes).decode('utf-8'),
                "receiver_public_key": base64.b64encode(receiver_public_key_bytes).decode('utf-8'),
                "encrypted_message": base64.b64encode(encrypted_message).decode('utf-8'),
            })

            client_socket.send(b"Message added to the blockchain.")
        elif action == 'retrieve_messages':
            # Retrieve the messages for the given sender's public key
            public_key_base64 = base64.b64encode(sender_public_key_bytes).decode('utf-8')
            messages = retrieve_messages(public_key_base64)
            client_socket.send(json.dumps(messages).encode('utf-8'))
        else:
            client_socket.send(b"Invalid action requested.")

    except Exception as e:
        print(f"Error handling client {client_address}: {e}")
        client_socket.send(b"An error occurred.")
    finally:
        client_socket.close()

def start_server():
    """Starts the server and listens for incoming client connections."""
    blockchain_state = list(load_last_block())

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 12345))
    server_socket.listen(5)
    print("Server is running...")

    while True:
        client_socket, client_address = server_socket.accept()
        threading.Thread(target=handle_client, args=(client_socket, client_address, blockchain_state)).start()

if __name__ == "__main__":
    start_server()