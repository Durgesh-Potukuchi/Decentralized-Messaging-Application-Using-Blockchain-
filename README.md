# Decentralized Messaging Application Using Blockchain ⛓️💬

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![Status](https://img.shields.io/badge/Status-Prototype-red?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)


> A decentralized, secure messaging application developed as a second-year project for our college project exhibition. This application uses RSA for end-to-end encryption and a simplified blockchain ledger to store message history, ensuring that communication is both private and immutable.

---

## ⚠️ Security Disclaimer
This project is a proof-of-concept and a learning exercise. It is **NOT SECURE** for real-world use. It contains several known security vulnerabilities.

**Please do not use this application for any sensitive or private communication.**

---

## ✨ Features

* 🔒 **End-to-End Encryption:** All messages are encrypted using a 2048-bit RSA public/private key pair.
* ⛓️ **Blockchain Ledger:** Messages are stored as transactions in a file-based blockchain, creating an immutable chat history.
* 💻 **Multi-Client Support:** The server uses threading to handle connections from multiple clients simultaneously.
* 🔑 **Automatic Key Generation:** The client application automatically generates RSA key pairs for new users.

---

## 🚧 Known Issues & Future Improvements

As a prototype, this project has several areas for improvement. The following are key issues that would need to be addressed for a production-ready system:

### Security Vulnerabilities
* **Lack of Authentication:** The server currently trusts the public key sent by the client. A malicious user could impersonate another user by sending their public key.
* **No Message Signing:** The sender of a message is not verified, making it possible for messages to be spoofed.
* **Vulnerability to Replay Attacks:** Captured network traffic could be re-sent to the server to duplicate messages on the blockchain.

### Performance & Usability
* **Inefficient Message Retrieval:** The server scans the entire blockchain file for every request, which is not scalable.
* **Manual Key Exchange:** Users must manually share their public key files to communicate.
* **Hardcoded Server IP:** The server's IP address is hardcoded in the client script.

---

## 🔮 Future Plans: Decentralized Governance

To enhance the decentralization of the network, we plan to implement a **voting system for new member registration**.

The proposed system would work as follows:
1.  A new user submits a request to join the network.
2.  This request is broadcast to all existing members as a proposal.
3.  Existing members can vote 'yes' or 'no' on adding the new user.
4.  If the proposal receives a majority of 'yes' votes, the new user's public key is officially added to the member list, granting them access to the network.

This would move the system away from a centralized server that accepts anyone, towards a community-governed network.

---

## 🛠️ Tech Stack

* **Language:** Python
* **Cryptography:** `rsa` library
* **Networking:** `socket` module for TCP communication
* **Concurrency:** `threading` module
* **File Integrity:** `filelock` for preventing race conditions

---

## 🏗️ System Architecture

The system follows a simple client-server model where the server's primary role is to maintain the blockchain and relay messages.

```
+-----------+                   +-----------------+                   +-----------+
|           |                   |                 |                   |           |
|  Client A |<----------------->|      Server     |<----------------->|  Client B |
|           |                   | (Blockchain Host) |                   |           |
+-----------+                   +-----------------+                   +-----------+
      |                                   |                                   |
      | Encrypted Msg                     |                                   |
      +---------------------------------->|                                   |
                                          | Add to Blockchain                 |
                                          |                                   |
                                          |       Retrieve Encrypted Msg      |
                                          |<----------------------------------+
```

---

## 🚀 Getting Started

Follow these steps to get the application running on your local machine.

### Prerequisites

* Python 3.9 or higher
* pip (Python package installer)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/your-repository-name.git](https://github.com/your-username/your-repository-name.git)
    cd your-repository-name
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

---

## 🏃‍♂️ How to Run

1.  **Start the Server:**
    Open a terminal and run the server script. It will start listening for connections.
    ```bash
    python server.py
    ```

2.  **Run the Client(s):**
    Open one or more new terminal windows and run the client script. Each instance will act as a separate user.
    ```bash
    python client.py
    ```
    Follow the on-screen prompts to register a username, send messages, and retrieve your message history.
