import socket
import threading

def start_client(server_ip="192.168.1.103", port=12345):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((server_ip, port))
    except:
        print("Unable to connect to the server.")
        return

    def receive_messages():
        while True:
            try:
                message = client.recv(1024).decode()
                if not message:
                    break
                print(message)
            except:
                print("Disconnected from server")
                break

    threading.Thread(target=receive_messages, daemon=True).start()

    username = input("Enter your name: ")
    client.send(username.encode())

    while True:
        message = input()

        if message.lower() == 'exit':
            client.close()
            break

        client.send(message.encode())

if __name__ == "__main__":
    start_client("192.168.1.103")  
