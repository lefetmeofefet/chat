import socket
import _thread
import uuid
import json
from datetime import datetime, timedelta
from .db import db
from .message import Message

HOST = "0.0.0.0"
PORT = 6668
SESSION_MINUTES = 60
SESSION_EXTENSION_MINUTES = 30


class ClientConnection:
    def __init__(self, client_socket, address):
        self.name = None
        self.room = None
        self.socket = client_socket
        self.address = address
        self.session_id = None
        self.session_expiration = None
        self.marked_for_deletion = False  # User when another client logs in with the same username


class Server:
    def __init__(self):
        self.client_connections = []
        self.room_to_clients = {}
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((HOST, PORT))
        self.server_socket.listen()
        print(f"Server is up and running on {self.server_socket.getsockname()}")

        while True:
            client_socket, address = self.server_socket.accept()
            client_connection = ClientConnection(client_socket, address)
            self.client_connections.append(client_connection)
            _thread.start_new_thread(self.client_thread, (client_connection,))

    @staticmethod
    def serialize_dict(dict_to_serialize):
        # the null byte is for delimiting multiple messages in the same 'socket.recv' call
        return json.dumps(dict_to_serialize, default=str).encode() + b'\0'

    def client_thread(self, client_connection: ClientConnection):
        print(f"Connected by {client_connection.address}")
        while True:
            try:
                requests = client_connection.socket.recv(1024)
                requests = requests[:-1]  # Remove the null byte at the end
                for request in requests.split(b"\0"):
                    print(f"Received {request}")
                    if not request or client_connection.marked_for_deletion:
                        self.disconnect_client(client_connection)
                        return
                    parsed_request = json.loads(request)
                    self.handle_request(client_connection, parsed_request)

            except ConnectionResetError as e:
                self.disconnect_client(client_connection)
                return

    def handle_request(self, client_connection, request):
        try:
            if request["type"] == "does_user_exist":
                self.handle_does_user_exist(request, client_connection)
            elif request["type"] in ["register", "login"]:
                self.handle_registration_and_login(request, client_connection)
            else:
                session_id = request["session_id"]
                if client_connection.session_id is None:
                    user = db.get_user(client_connection.name)
                    client_connection.session_id = user["session_id"]
                    client_connection.session_expiration = user["session_expiration"]

                if session_id == client_connection.session_id and datetime.utcnow() < client_connection.session_expiration:
                    self.extend_user_session_if_needed(client_connection)
                    if request["type"] == "enter_room":
                        self.handle_enter_room(request, client_connection)
                    elif request["type"] == "message":
                        self.handle_message(request, client_connection)
                    elif request["type"] == "seen_message":
                        self.handle_received_message(request, client_connection)
                else:
                    print("Request rejected because of invalid session_id")
                    client_connection.socket.sendall(self.serialize_dict({
                        "type": "error",
                        "error": "Session expired! please restart chat and login again"
                    }))
        except Exception as e:
            print("Unexpected error: " + str(e))
            client_connection.socket.sendall(self.serialize_dict({
                "type": "error",
                "error": "Server error: " + str(e)
            }))

    def extend_user_session_if_needed(self, client_connection):
        if client_connection.session_expiration - datetime.utcnow() <= timedelta(minutes=SESSION_EXTENSION_MINUTES):
            db.set_user_session(client_connection.name, client_connection.session_id, datetime.utcnow() + timedelta(minutes=SESSION_MINUTES))

    def handle_does_user_exist(self, request, client_connection):
        user_name = request["name"]
        user_exists = db.does_user_exist(user_name)
        client_connection.socket.sendall(self.serialize_dict({
            "user_exists": user_exists
        }))

    def handle_registration_and_login(self, request, client_connection: ClientConnection):
        name = request["name"]
        password_hash = request["password_hash"]
        user = db.get_user(name)
        session_id = str(uuid.uuid4())
        session_expiration = datetime.utcnow() + timedelta(minutes=SESSION_MINUTES)
        if user is None:  # Registration
            db.create_user(name, password_hash, session_id, session_expiration)
        elif user["password_hash"] == password_hash:  # Login
            db.set_user_session(name, session_id, session_expiration)
        else:  # Wrong password
            client_connection.socket.sendall(self.serialize_dict({
                "type": "error",
                "error": "Wrong password!"
            }))
            return
        client_connection.name = name
        client_connection.session_id = session_id
        client_connection.session_expiration = session_expiration
        client_connection.socket.sendall(self.serialize_dict({"session_id": session_id}))

        # Check if this username is already connected and disconnect it
        for existing_connection in self.client_connections:
            if existing_connection.name == name and existing_connection is not client_connection:
                self.disconnect_client(existing_connection)
                existing_connection.marked_for_deletion = True

    def handle_enter_room(self, request, client_connection):
        room = request["room"]
        if room in self.room_to_clients:
            self.room_to_clients[room].append(client_connection)
        else:
            self.room_to_clients[room] = [client_connection]
        client_connection.room = room
        client_connection.socket.sendall(self.serialize_dict({
            "type": "messages_history",
            "messages": [m.to_dict() for m in db.get_messages(room)]
        }))

    def handle_message(self, request, client_connection: ClientConnection):
        message = Message(
            text=request["text"],
            sender_name=client_connection.name,
            time=datetime.utcnow(),
            seen_by=[]
        )
        db.save_message(message, client_connection.room)
        serialized_message = self.serialize_dict({
            "type": "message",
            "message": message.to_dict()
        })

        # Send message to all clients in the room
        clients_in_room = self.room_to_clients[client_connection.room]
        for c in clients_in_room:
            c.socket.sendall(serialized_message)

    def handle_received_message(self, request, client_connection: ClientConnection):
        clients_in_room = self.room_to_clients[client_connection.room]
        message_id = request["message_id"]
        db.update_seen_by(message_id, client_connection.name)
        serialized_message = self.serialize_dict({
            "type": "seen_message",
            "message_id": message_id,
            "seen_by": client_connection.name
        })
        for c in clients_in_room:
            if c is not client_connection:  # No need to send "seen" back to the seer
                c.socket.sendall(serialized_message)

    def disconnect_client(self, client_connection):
        print(f"Client {client_connection.address} disconnected")
        self.client_connections.remove(client_connection)
        if client_connection.room in self.room_to_clients:
            self.room_to_clients[client_connection.room].remove(client_connection)
