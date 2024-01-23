import os
import socket

import communication_utils as comm_utils
import file_utils as f_utils


def print_help():
    """Display a list with all the commands the client can use."""
    print(
        "\n- Arguments with [] are optional."
        + " If not specified, it will default to current directory."
    )
    print("Available Operations:")
    print("/help\n\t- Display this text.")
    print(
        "/list [<directory>] or /ls [<directory>]\n"
        + "\t- Display files in the specified directory."
    )
    print(
        "/tree [<directory>]\n"
        + "\t- Display files in the specified directory in a tree shape. It also displays the content of every subdirectory recursivelly."
    )
    print(
        "/upload <local_file_path> [<server_directory>]\n"
        + "\t- Send a file to the server."
    )
    print(
        "/download <server_file_path> [<local_directory>]\n"
        + "\t- Get a copy of a file from the server."
    )
    print("/delete <server_file_path>\n\t- Delete a file from the server.")
    print("/exit\n\t- Close the connection to the server.")
    print()


def send_request(client_socket: socket.socket, command: str, opt_arg: str | None):
    """
    Send a string to the server.

    It may be a command or a command and arguments. The function waits for a permission from the
    server to proceed.
    """
    message = f"{command} {opt_arg}" if opt_arg else command
    package = f_utils.text_message_encode(message)
    client_socket.sendall(package)
    permission_check = comm_utils.receive_text(client_socket)
    if permission_check != "ok":
        raise PermissionError(permission_check)


def validate_command(client_socket: socket.socket, command: str, file: str | None) -> bool:
    """
    Validates a command requested from the client.

    If a file argument is provided, checks with the server if the file exists and adjusts the prompt
    to confirm with the client whether they really want to perform the operation. The case in which
    the file is None is only used to ask whether the client wants to exit.

    If the server reports that the file doesn't exist, it raises an error.
    """
    if file:
        file_type = comm_utils.receive_text(client_socket)
        # When the client requests an upload, the server always reports the file type as directory.
        # We need to check locally and inform the server to prevent an invalid operation.
        if command == "/upload":
            file_type = (
                "dir" if os.path.isdir(file) else "file" if os.path.isfile(file) else "not_found"
            )
            # Inform the server if the file was not found locally.
            if file_type == "not_found":
                comm_utils.send_text(client_socket, "error")
                comm_utils.send_text(client_socket, file)
                raise FileNotFoundError(f"Error: '{file}' not found")

        # command[1:] removes the leading "/" from the command to make a cleaner prompt.
        if file_type == "dir":
            prompt = f"'{file}' is a directory. Are you sure you want to {command[1:]} it? [Y/n] "
        elif file_type == "not_found":
            raise FileNotFoundError(comm_utils.receive_text(client_socket))
        else:
            prompt = f"Are you sure you want to {command[1:]} '{file}'? [Y/n] "
    else:
        prompt = f"Are you sure you want to {command[1:]}? [Y/n] "

    # Confirm if the user wants to proceed with the action. Defaults to yes.
    user_input = input(prompt)
    if not user_input or user_input[0].lower() == "y":
        comm_utils.send_text(client_socket, "y")
        return True
    else:
        comm_utils.send_text(client_socket, "n")
        return False
