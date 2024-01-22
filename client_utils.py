import socket

import file_utils as f_utils
import communication_utils as comm_utils


def print_help():
    print(
        "\n- Arguments with [] are optional."
        + " If not specified, it will default to current directory."
    )
    print("Available Operations:")
    print("/help\n\t- Display this text.")
    print(
        "/list [<directory>] or /ls [<directory>]\n"
        + "\t- Display files and subdirectories in the specified directory."
    )
    print(
        "/tree [<directory>]\n"
        + "\t- Display available files in the specified directory."
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
    print(
        "/cd <subdirectory>\n\t- Change current directory on the server."
        + "\n\t- Empty argument will go back to the main directory."
    )
    print("/exit\n\t- Close the connection to the server.")
    print()


def send_request(client_socket: socket.socket, command: str, opt_arg: str | None):
    """
    Send a string to the server. It may be a command or a command and arguments.
    """
    message = command
    if opt_arg:
        message += " " + opt_arg
    package = f_utils.text_message_encode(message)
    client_socket.sendall(package)


def validate_command(client_socket: socket.socket, command: str, file: str | None) -> bool:
    if file:
        file_type = comm_utils.receive_text(client_socket)
        if file_type == "dir":
            user_input = input(f"{file} is a directory. Are you sure you want to {command[1:]} it? [Y/n] ")
        else:
            user_input = input(f"Are you sure you want to {command[1:]} {file}? [Y/n] ")
        if not user_input or user_input[0].lower() == "y":
            comm_utils.send_text(client_socket, "y")
        else:
            comm_utils.send_text(client_socket, "n")
    else:
        user_input = input(f"Are you sure you want to {command[1:]}? [Y/n] ")

    if not user_input:
        return True
    return user_input[0].lower() == "y"


def validate_dir_action(command: str) -> bool:
    user_input = input(
        f"The selected file is a directory. Do you want to {command[1:]} the whole directory? [Y/n] "
    )

    if not user_input:
        return True
    return user_input[0].lower() == "y"
