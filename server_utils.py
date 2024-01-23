import os
import socket

import communication_utils as comm_utils
dtprint = comm_utils.timestamped_print

CHUNK_SIZE = 1024
TIMESTMP_OFFSET = 22


def receive_request(client_socket: socket.socket) -> list:
    """Receives a command from the client as text and returns it as a list of strings."""
    request = comm_utils.receive_text(client_socket)
    return request.split()


def confirm_filetype_with_client(client_socket: socket.socket, file_path: str) -> bool:
    """
    Sends to the client which type of file they're requesting and waits for the validation from the
    client side to continue with the operation.
    """
    if os.path.isdir(file_path):
        comm_utils.send_text(client_socket, "dir")
    elif os.path.isfile(file_path):
        comm_utils.send_text(client_socket, "file")
    else:
        comm_utils.send_text(client_socket, "not_found")
        raise FileNotFoundError(f"Error: '{os.path.basename(file_path)}' not found")

    client_feedback = comm_utils.receive_text(client_socket)
    # Checks if the client reported an error. This situation occurs only when the client has
    # requested an upload, as the server cannot directly identify the error in this case. Since the
    # error was already raised by the client, the server mimics the error output for logging
    # purposes.
    if client_feedback == "error":
        wrong_file_requested = comm_utils.receive_text(client_socket)
        fe = f"Error: '{wrong_file_requested}' not found"
        dtprint(f"File error. Sending to client the report:\n{' '*TIMESTMP_OFFSET}'{fe}'")
    return client_feedback == "y"
