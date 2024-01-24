import os
import socket

import communication_utils as comm_utils
import file_utils as f_utils

dtprint = comm_utils.timestamped_print

TIMESTMP_OFFSET = " " * 24
HOME_DIR = os.getcwd()


def receive_request(client_socket: socket.socket) -> list:
    """Receives a command from the client as text and returns it as a list of strings."""
    request = comm_utils.receive_text(client_socket)
    return request.split()


def confirm_filetype_with_client(
    client_socket: socket.socket, client_address: tuple, file_path: str
) -> bool:
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
        dtprint(
            f"File error. Sending the report to client {client_address}:\n{TIMESTMP_OFFSET}'{fe}'"
        )
    return client_feedback == "y"


def handle_client(client_socket: socket.socket, client_address: tuple):
    """
    Function to handle each client connection in a separate thread.
    """
    comm_utils.send_text(client_socket, "Connection accepted")
    dtprint(f"Connection from {client_address} accepted.")

    # Run the server requests until client exits.
    while True:
        requests = receive_request(client_socket)
        request_type, arg1, *_ = requests + [None]
        dtprint(f"Client {client_address} requested '{request_type[1:]}' command.")

        try:
            if arg1:
                full_path = os.path.abspath(os.path.join(os.getcwd(), arg1))

                if not full_path.startswith(HOME_DIR):
                    raise PermissionError(
                        f"Error: You don't have permission to access that directory"
                    )
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
                            "/tree": f_utils.tree_list_content,
                        }
                        dir_list = listing_function[request_type](full_path)

                        comm_utils.send_text(client_socket, "ok")
                        comm_utils.send_text(client_socket, dir_list)

                        prompt = f"Listed a directory for client {client_address}"
                        prompt += " as a tree." if request_type == "/tree" else "."
                        dtprint(prompt)

                    except FileNotFoundError:
                        comm_utils.send_text(client_socket, "FILEError")
                        raise FileNotFoundError(
                            f"Error: '{os.path.basename(full_path)}' not found"
                        )
                    except OSError as oe:
                        comm_utils.send_text(client_socket, "OSError")
                        raise OSError(
                            f"Error: OS related error. Maybe your path wasn't a directory?"
                        )
                case "/exit":
                    if comm_utils.receive_text(client_socket) == "y":
                        dtprint(f"Client {client_address} closed the connection with the server.")
                        break
                case "/upload":
                    if confirm_filetype_with_client(client_socket, client_address, full_path):
                        dtprint(f"Receiving a file from the client {client_address}.")
                        comm_utils.receive_file(client_socket, arg1)
                        print(f"{TIMESTMP_OFFSET}(From client {client_address}.")
                case "/download":
                    if confirm_filetype_with_client(client_socket, client_address, full_path):
                        dtprint(f"Sending a file to the client {client_address}.")
                        comm_utils.send_file(client_socket, full_path)
                        print(f"{TIMESTMP_OFFSET}(From client {client_address}.")
                case "/delete":
                    if confirm_filetype_with_client(client_socket, client_address, full_path):
                        f_utils.delete_file(full_path)
                        comm_utils.send_text(client_socket, f"'{arg1}' deleted successfully.")
                        dtprint(
                            f"Deleted the file '{arg1}'. (Requested from client {client_address})"
                        )
                case "missarg":
                    dtprint(
                        f"Client {client_address} action was cancelled due to missing arguments."
                    )

        except FileNotFoundError as fe:
            dtprint(
                f"File error. Sending the report to client {client_address}:\n{TIMESTMP_OFFSET}'{fe}'"
            )
            comm_utils.send_text(client_socket, f"{fe}")
        except PermissionError as pe:
            dtprint(
                f"Client error. Sending the report to client {client_address}:\n{TIMESTMP_OFFSET}'{pe}'"
            )
            comm_utils.send_text(client_socket, f"{pe}")
        except BrokenPipeError:
            dtprint(
                f"Client error: The client {client_address} has closed the connection unexpectedly."
            )
        except OSError as oe:
            dtprint(
                f"OS related error. Sending the report to client {client_address}:\n{TIMESTMP_OFFSET}'{oe}'"
            )
            comm_utils.send_text(client_socket, f"{oe}")

    # Close the connection for this client
    client_socket.close()
    dtprint(f"Connection with {client_address} closed.")
