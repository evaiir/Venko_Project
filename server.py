import os
import socket

import communication_utils as comm_utils
import file_utils as f_utils
import server_utils as sv_utils

dtprint = comm_utils.timestamped_print

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
dtprint(f"Server listening on any interface on port {port}")

# Accept a connection.
client_socket, client_address = server_socket.accept()
dtprint(f"Connection from {client_address} accepted.")

# Run the server requests until client exits.
while True:
    requests = sv_utils.receive_request(client_socket)
    request_type, arg1 = requests[:2] + [None] * (2 - len(requests))

    match request_type:
        case "/list" | "/ls":
            dir_list = f_utils.list_content(arg1)
            comm_utils.send_text(client_socket, dir_list)
            dtprint(f"Listed a directory for client {client_address}.")
        case "/tree":
            tree_list = f_utils.tree_list_content(arg1)
            comm_utils.send_text(client_socket, tree_list)
            dtprint(f"Listed a directory for client {client_address} as a tree.")
        case "/exit":
            dtprint(f"Client {client_address} closed the connection with the server.")
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
                except ValueError as e:
                    comm_utils.send_text(client_socket, f"{e}")
        case "/delete":
            file_path = os.path.join(HOME_DIR, arg1)
            if sv_utils.confirm_filetype_with_client(client_socket, file_path):
                try:
                    f_utils.delete_file(file_path)
                    comm_utils.send_text(client_socket, f"{arg1} deleted successfully.")
                    dtprint(
                        f"Deleted the file {arg1}. (Requested from client {client_address})"
                    )
                except ValueError as e:
                    comm_utils.send_text(client_socket, f"{e}")
        case "/cd":
            if arg1:
                file_path = os.path.join(HOME_DIR, arg1)
                try:
                    sv_utils.change_directory(file_path)
                    comm_utils.send_text(
                        client_socket, "Directory changed successfully."
                    )
                    dtprint(f"I changed to another directory for client {client_address}")
                except ValueError as e:
                    dtprint(f"Error: {e}")
                    comm_utils.send_text(client_socket, f"Error: {e}")
            else:
                sv_utils.change_directory(HOME_DIR)
                comm_utils.send_text(client_socket, "Directory changed successfully.")
                dtprint(f"I changed to another directory for client {client_address}")


# Close the connection
client_socket.close()
server_socket.close()
