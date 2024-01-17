import socket

import server_module as sm
import client_module as cm

# Server configuration
host = "192.168.1.4"
port = 8080

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
client_socket.connect((host, port))

# Greet
print(f"Connected to {host}:{port}")
print("Type /help to list the available operations.")

# Send requests to the server until operation /exit is called.
while True:
    # Empty (optional) args are handled inside each function
    commands = input("New command: ").split()
    command_type, arg1, arg2 = commands[:3] + [None] * (3 - len(commands))

    match command_type:
        case "/help":
            cm.print_help()
        case "/exit":
            cm.send_request(client_socket, command_type, None)
            break
        case "/list" | "/ls" | "/tree":
            cm.send_request(client_socket, command_type, arg1)
            message = sm.receive_text(client_socket)
            print(message)
        case "/upload":
            cm.send_request(client_socket, command_type, arg2)
            sm.send_file(client_socket, arg1)
        case "/download":
            cm.send_request(client_socket, command_type, arg1)
            sm.receive_file(client_socket, arg2)
        case "/delete" | "/cd":
            cm.send_request(client_socket, command_type, arg1)
        case None:
            print("Error: Empty command.")


# Close the connection
client_socket.close()
