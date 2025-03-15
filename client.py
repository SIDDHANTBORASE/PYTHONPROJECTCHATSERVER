import socket
import threading
import sys

def start_client(host='192.168.1.100', port=12345):  # Use the server's actual IP
    """Connect to the chat server and handle sending/receiving messages."""
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host, port))
        print(f"🔗 Connected to chat server at {host}:{port}\n")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return

    def receive_messages():
        """Listen for incoming messages and display them properly."""
        while True:
            try:
                message = client.recv(1024).decode()
                if not message:
                    break
                sys.stdout.write(f"\r📨 {message}\nYou: ")  
                sys.stdout.flush()
            except:
                print("\n❌ Disconnected from server.")
                client.close()
                break

    threading.Thread(target=receive_messages, daemon=True).start()
    
    print("💬 Type your messages below. Type 'exit' to disconnect.\n")
    while True:
        message = input("You: ")
        if message.lower() == 'exit':
            print("👋 Disconnecting...")
            client.close()
            break
        client.send(message.encode())

if __name__ == "__main__":
    start_client()
