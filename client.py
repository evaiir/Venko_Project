import socket

import client_utils as cl_utils
import communication_utils as comm_utils

dtprint = comm_utils.timestamped_print

# Server configuration
host = "192.168.1.4"
port = 8080

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
client_socket.connect((host, port))

# Greet
dtprint(f"Connected to {host}:{port}")
print("Type /help to list the available operations.")

# Send requests to the server until operation /exit is called.
while True:
    # Empty (optional) args are handled inside each function
    commands = input("New command: ").split()
    command_type, arg1, arg2 = commands[:3] + [None] * (3 - len(commands))

    match command_type:
        case "/help":
            cl_utils.print_help()
        case "/exit":
            if cl_utils.validate_command(client_socket, command_type, None):
                cl_utils.send_request(client_socket, command_type, None)
                break
        case "/list" | "/ls" | "/tree":
            cl_utils.send_request(client_socket, command_type, arg1)
            message = comm_utils.receive_text(client_socket)
            print(message)
        case "/upload":
            if arg1:
                cl_utils.send_request(client_socket, command_type, arg2)
                if cl_utils.validate_command(client_socket, command_type, arg1):
                    comm_utils.send_file(client_socket, arg1)
            else:
                dtprint("Error: No file specified to be uploaded.")
        case "/download":
            if arg1:
                cl_utils.send_request(client_socket, command_type, arg1)
                if cl_utils.validate_command(client_socket, command_type, arg1):
                    comm_utils.receive_file(client_socket, arg2)
            else:
                dtprint("Error: No file specified to be downloaded.")
        case "/delete":
            if arg1:
                cl_utils.send_request(client_socket, command_type, arg1)
                cl_utils.validate_command(client_socket, command_type, arg1)
                feedback = comm_utils.receive_text(client_socket)
                print(feedback)
            else:
                dtprint("Error: No file specified to be deleted.")
        case  "/cd":
            cl_utils.send_request(client_socket, command_type, arg1)
            answer = comm_utils.receive_text(client_socket)
            print(answer)
        case None:
            dtprint("Error: Empty command.")


# Close the connection
client_socket.close()
