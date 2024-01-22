import socket
import os

import file_utils as f_utils
import server_utils as sv_utils
import communication_utils as comm_utils

HOME_DIR = os.getcwd()

# Server configuration.
host = str(socket.INADDR_ANY)  # Bind to any interface
port = 8080

# Create a socket object.
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to a specific address and port.
server_socket.bind((host, port))

# Listen for incoming connections (currently only one at a time).
server_socket.listen(1)
print(f"Server listening on any interface on port {port}")

# Accept a connection.
client_socket, client_address = server_socket.accept()
print(f"Connection from {client_address} accepted.")

# Run the server requests until client exits.
while True:
    requests = sv_utils.receive_request(client_socket)
    request_type, arg1 = requests[:2] + [None] * (2 - len(requests))
    print(f"I got those arguments from the request: {requests}")

    match request_type:
        case "/list" | "/ls":
            dir_list = f_utils.list_content(arg1)
            comm_utils.send_text(client_socket, dir_list)
            print(f"I listed a directory for client {client_address} normally.")
        case "/tree":
            tree_list = f_utils.tree_list_content(arg1)
            comm_utils.send_text(client_socket, tree_list)
            print(f"I listed a directory for client {client_address} as a tree.")
        case "/exit":
            print(f"Client {client_address} exited from server.")
            break
        case "/upload":
            file_path = os.path.join(HOME_DIR, arg1) if arg1 else HOME_DIR
            if sv_utils.confirm_filetype_with_client(client_socket, file_path):
                try:
                    comm_utils.receive_file(client_socket, arg1)
                except ValueError as e:
                    comm_utils.send_text(client_socket, f"{e}")
        case "/download":
            file_path = os.path.join(HOME_DIR, arg1)
            if sv_utils.confirm_filetype_with_client(client_socket, file_path):
                try:
                    comm_utils.send_file(client_socket, file_path)
                    print("I sent a file!")
                except ValueError as e:
                    comm_utils.send_text(client_socket, f"{e}")
        case "/delete":
            file_path = os.path.join(HOME_DIR, arg1)
            if sv_utils.confirm_filetype_with_client(client_socket, file_path):
                try:
                    f_utils.delete_file(arg1)
                    comm_utils.send_text(client_socket, f"{arg1} deleted successfully.")
                    print(f"I deleted a file. (Requested from client {client_address})")
                except ValueError as e:
                    comm_utils.send_text(client_socket, f"{e}")
        case "/cd":
            if arg1:
                file_path = os.path.join(HOME_DIR, arg1)
                try:
                    sv_utils.change_directory(file_path)
                    comm_utils.send_text(client_socket, "Directory changed successfully.")
                    print(f"I changed to another directory for client {client_address}")
                except ValueError as e:
                    print(f"Error: {e}")
                    comm_utils.send_text(client_socket, f"Error: {e}")
            else:
                sv_utils.change_directory(HOME_DIR)
                comm_utils.send_text(client_socket, "Directory changed successfully.")
                print(f"I changed to another directory for client {client_address}")


# Close the connection
client_socket.close()
server_socket.close()
