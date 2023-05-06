import socket
import _thread
import uuid
import json
from .message import Message

HOST = "0.0.0.0"
PORT = 6668


class ClientConnection:
    def __init__(self, client_socket, address):
        self.socket = client_socket
        self.address = address


class Server:
    def __init__(self):
        self.client_connections = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((HOST, PORT))
        self.server_socket.listen()
        print(f"Server is up and running on {self.server_socket.getsockname()}")

        while True:
            client_socket, address = self.server_socket.accept()
            client_connection = ClientConnection(client_socket, address)
            self.client_connections.append(client_connection)
            _thread.start_new_thread(self.client_thread, (client_connection,))

    def client_thread(self, client_connection: ClientConnection):
        print(f"Connected by {client_connection.address}")
        while True:
            try:
                data = client_connection.socket.recv(1024)
                print(f"Received {data}")
                if not data:
                    print(f"Client {client_connection.address} disconnected")
                    self.client_connections.remove(client_connection)
                    return
            except ConnectionResetError as e:
                print(f"Disconnected from {client_connection.address}")
                self.client_connections.remove(client_connection)
                return

            parsed_data = json.loads(data)
            message = Message(
                text=parsed_data["text"],
                sender_name=str(client_connection.address),
                time="now",
                seen_by=[]
            )
            serialized_message = message.serialize()
            # Send message to all clients
            for c in self.client_connections:
                c.socket.sendall(serialized_message)
