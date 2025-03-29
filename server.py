import socket
import threading

class ChatServer:
    def __init__(self, host='0.0.0.0', port=12345):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        self.server.bind((host, port))
        self.server.listen(5)
        
        self.clients = {} 
        self.rooms = {}   

        print(f"Server started on {host}:{port}")

    def broadcast(self, message, sender_socket=None, room=None):
        """Send message to all clients in the room or globally."""
        targets = []
        
        if room:
            targets = self.rooms.get(room, [])
        else:
            targets = self.clients.keys()

        for client in targets:
            if client != sender_socket:
                try:
                    client.send(message.encode())
                except:
                    self.remove_client(client)

    def send_private_message(self, sender_socket, recipient, message):
        """Send a direct message (DM) to a specific user."""
        sender_name = self.clients[sender_socket]['username']

        recipient_socket = None
        for client, data in self.clients.items():
            if data['username'] == recipient:
                recipient_socket = client
                break

        if recipient_socket:
            try:
                recipient_socket.send(f"[DM from {sender_name}]: {message}".encode())
                sender_socket.send(f"[DM to {recipient}]: {message}".encode())
            except:
                sender_socket.send("Failed to send DM.".encode())
        else:
            sender_socket.send(f"User '{recipient}' not found.".encode())

    def join_room(self, client_socket, room_name):
        """Add client to a room."""
        current_room = self.clients[client_socket]['room']
        if current_room:
            self.rooms[current_room].remove(client_socket)
            self.broadcast(f"{self.clients[client_socket]['username']} left {current_room}", room=current_room)

        self.clients[client_socket]['room'] = room_name

        if room_name not in self.rooms:
            self.rooms[room_name] = []

        self.rooms[room_name].append(client_socket)
        self.broadcast(f"{self.clients[client_socket]['username']} joined {room_name}", room=room_name)

    def leave_room(self, client_socket):
        """Remove client from the current room."""
        current_room = self.clients[client_socket]['room']
        if current_room:
            self.rooms[current_room].remove(client_socket)
            self.broadcast(f"{self.clients[client_socket]['username']} left {current_room}", room=current_room)
            
            self.clients[client_socket]['room'] = None

    def remove_client(self, client_socket):
        """Remove client from chat and close the socket."""
        if client_socket in self.clients:
            username = self.clients[client_socket]['username']
            current_room = self.clients[client_socket]['room']

            print(f"{username} has disconnected.")
            
            if current_room:
                self.rooms[current_room].remove(client_socket)

            del self.clients[client_socket]
            
            client_socket.close()
            self.broadcast(f"{username} has left the chat.", sender_socket=None)

    def handle_client(self, client_socket):
        """Handle communication with a client."""
        try:
            client_socket.send("Enter your name: ".encode())
            username = client_socket.recv(1024).decode().strip()

            self.clients[client_socket] = {'username': username, 'room': None}
            
            print(f"{username} has joined the chat.")
            
            # Notify others
            self.broadcast(f"{username} has joined the global chat.", sender_socket=client_socket)

            client_socket.send("Welcome! Use '/join <room>' to enter a room or '/dm <user>' for DMs.".encode())

            while True:
                message = client_socket.recv(1024).decode().strip()
                if not message:
                    break

                if message.startswith("/dm"):
                    parts = message.split(" ", 2)
                    if len(parts) < 3:
                        client_socket.send("Usage: /dm <username> <message>".encode())
                    else:
                        _, recipient, dm_message = parts
                        self.send_private_message(client_socket, recipient, dm_message)

                elif message.startswith("/join"):
                    _, room_name = message.split(" ", 1)
                    self.join_room(client_socket, room_name)

                elif message.startswith("/leave"):
                    self.leave_room(client_socket)

                elif message.startswith("/global"):
                    self.leave_room(client_socket)
                    self.broadcast(f"{username} is back in the global chat.", sender_socket=client_socket)

                else:
                    current_room = self.clients[client_socket]['room']
                    if current_room:
                        self.broadcast(f"{username}: {message}", room=current_room)
                    else:
                        self.broadcast(f"{username}: {message}", sender_socket=client_socket)

        except:
            pass
        finally:
            self.remove_client(client_socket)

    def run(self):
        """Accept and handle clients."""
        while True:
            client_socket, _ = self.server.accept()
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

if __name__ == "__main__":
    server = ChatServer()
    server.run()
