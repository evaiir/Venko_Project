import socket

import client_utils as cl_utils
import communication_utils as comm_utils

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
            cl_utils.print_help()
        case "/exit":
            confirmation = cl_utils.validate_command(command_type, None)
            if confirmation:
                cl_utils.send_request(client_socket, command_type, None)
                break
        case "/list" | "/ls" | "/tree":
            cl_utils.send_request(client_socket, command_type, arg1)
            message = comm_utils.receive_text(client_socket)
            print(message)
        case "/upload":
            if arg1:
                if cl_utils.validate_command(command_type, arg1):
                    cl_utils.send_request(client_socket, command_type, arg2)
                    file_type = comm_utils.receive_text(client_socket)
                    if file_type == "dir":
                        if cl_utils.validate_dir_action(command_type):
                            comm_utils.send_text(client_socket, "y")
                            comm_utils.send_file(client_socket, arg1)
                    else:
                        comm_utils.send_text(client_socket, "y")
                        comm_utils.send_file(client_socket, arg1)
            else:
                print("Error: No file specified to be uploaded.")
        case "/download":
            if arg1:
                if cl_utils.validate_command(command_type, arg1):
                    cl_utils.send_request(client_socket, command_type, arg1)
                    file_type = comm_utils.receive_text(client_socket)
                    if file_type == "dir":
                        if cl_utils.validate_dir_action(command_type):
                            comm_utils.send_text(client_socket, "y")
                            comm_utils.receive_file(client_socket, arg2)
                    else:
                        comm_utils.send_text(client_socket, "y")
                        comm_utils.receive_file(client_socket, arg2)
            else:
                print("Error: No file specified to be downloaded.")
        case "/delete":
            if arg1:
                if cl_utils.validate_command(command_type, arg1):
                    cl_utils.send_request(client_socket, command_type, arg1)
                    file_type = comm_utils.receive_text(client_socket)
                    if file_type == "dir":
                        if cl_utils.validate_dir_action(command_type):
                            comm_utils.send_text(client_socket, "y")
                        else:
                            comm_utils.send_text(client_socket, "n")
                    else:
                        comm_utils.send_text(client_socket, "y")
            else:
                print("Error: No file specified to be deleted.")
        case  "/cd":
            cl_utils.send_request(client_socket, command_type, arg1)
            answer = comm_utils.receive_text(client_socket)
            print(answer)
        case None:
            print("Error: Empty command.")


# Close the connection
client_socket.close()
