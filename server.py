import socket
import threading

class ChatServer:
    def __init__(self, host='0.0.0.0', port=12345):  # Accept connections from any network
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(5)
        self.clients = []
        print(f"📡 Server started on {host}:{port}\n")

    def broadcast(self, message, sender_socket):
        """Send a message to all connected clients except the sender."""
        for client in self.clients:
            if client != sender_socket:
                try:
                    client.send(message)
                except:
                    self.clients.remove(client)

    def handle_client(self, client_socket, client_address):
        """Handle incoming messages from a client and broadcast them."""
        print(f"✅ New connection from {client_address}\n")
        while True:
            try:
                message = client_socket.recv(1024)
                if message:
                    print(f"📩 {client_address} says: {message.decode()}")
                    self.broadcast(message, client_socket)
                else:
                    break
            except:
                break
        
        print(f"❌ Client {client_address} disconnected.\n")
        self.clients.remove(client_socket)
        client_socket.close()

    def run(self):
        """Accept new client connections and start a thread for each client."""
        print("🚀 Chat server is running...\n")
        while True:
            client_socket, client_address = self.server.accept()
            self.clients.append(client_socket)
            threading.Thread(target=self.handle_client, args=(client_socket, client_address)).start()

if __name__ == "__main__":
    ChatServer().run()
