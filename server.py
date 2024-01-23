import os
import socket

import communication_utils as comm_utils
import file_utils as f_utils
import server_utils as sv_utils

dtprint = comm_utils.timestamped_print

HOME_DIR = os.getcwd()
MAX_CLIENTS = 1
TIMESTMP_OFFSET = 22

# Server configuration.
host = str(socket.INADDR_ANY)  # Bind to any interface
port = 8080

# Create a socket object.
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to a specific address and port.
server_socket.bind((host, port))

# Listen for incoming connections (currently only one at a time).
server_socket.listen(MAX_CLIENTS)
dtprint(f"Server listening on any interface on port {port}")

# Accept a connection.
client_socket, client_address = server_socket.accept()
dtprint(f"Connection from {client_address} accepted.")

# Run the server requests until client exits.
while True:
    requests = sv_utils.receive_request(client_socket)
    request_type, arg1, *_ = requests + [None]
    dtprint(f"Client {client_address} requested '{request_type[1:]}' command.")

    try:
        if arg1:
            full_path = os.path.abspath(os.path.join(os.getcwd(), arg1))

            if not full_path.startswith(HOME_DIR):
                raise PermissionError(f"Error: You don't have permission to access that directory")
            comm_utils.send_text(client_socket, "ok")
        else:
            full_path = HOME_DIR
            comm_utils.send_text(client_socket, "ok")

        match request_type:
            # Both listing functions have to check for error as they don't pass through the
            # validation function.
            case "/list" | "/ls" | "/tree":
                try:
                    listing_function = {
                        "/ls": f_utils.list_content,
                        "/list": f_utils.list_content,
                        "/tree": f_utils.tree_list_content
                    }
                    dir_list = listing_function[request_type](full_path)

                    comm_utils.send_text(client_socket, "ok")
                    comm_utils.send_text(client_socket, dir_list)

                    prompt = f"Listed a directory for client {client_address}"
                    prompt += " as a tree." if request_type == "/tree" else "."
                    dtprint(prompt)

                except FileNotFoundError:
                    comm_utils.send_text(client_socket, "FILEError")
                    raise FileNotFoundError(f"Error: '{os.path.basename(full_path)}' not found")
                except OSError as oe:
                    comm_utils.send_text(client_socket, "OSError")
                    raise OSError(f"Error: OS related error. Maybe your path wasn't a directory?")
            case "/exit":
                if comm_utils.receive_text(client_socket) == "y":
                    dtprint(f"Client {client_address} closed the connection with the server.")
                    break
            case "/upload":
                if sv_utils.confirm_filetype_with_client(client_socket, full_path):
                    dtprint(f"Receiving a file from the client {client_address}.")
                    comm_utils.receive_file(client_socket, arg1)
            case "/download":
                if sv_utils.confirm_filetype_with_client(client_socket, full_path):
                    dtprint(f"Sending a file to the client {client_address}.")
                    comm_utils.send_file(client_socket, full_path)
            case "/delete":
                if sv_utils.confirm_filetype_with_client(client_socket, full_path):
                    f_utils.delete_file(full_path)
                    comm_utils.send_text(client_socket, f"'{arg1}' deleted successfully.")
                    dtprint(
                        f"Deleted the file '{arg1}'. (Requested from client {client_address})"
                    )
            case "missarg":
                dtprint(f"Client {client_address} action was cancelled due to missing arguments.")

    except FileNotFoundError as fe:
        dtprint(f"File error. Sending to client the report:\n{' '*TIMESTMP_OFFSET}'{fe}'")
        comm_utils.send_text(client_socket, f"{fe}")
    except PermissionError as pe:
        dtprint(f"Client error. Sending to client the report:\n{' '*TIMESTMP_OFFSET}'{pe}'")
        comm_utils.send_text(client_socket, f"{pe}")
    except BrokenPipeError as be:
        dtprint(
            f"Client error: The client {client_address} has closed the connection unexpectedly."
        )
    except OSError as oe:
        dtprint(f"OS related error. Sending to client the report:\n{' '*TIMESTMP_OFFSET}'{oe}'")
        comm_utils.send_text(client_socket, f"{oe}")


# Close the connection
client_socket.close()
server_socket.close()
