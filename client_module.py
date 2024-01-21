import socket

import file_handling_module as fhm


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
    print("/cd <directory>\n\t- Change current directory on the server.")
    print("/exit\n\t- Close the connection to the server.")
    print()


def send_request(client_socket: socket.socket, command: str, opt_arg: str | None):
    message = command
    if opt_arg:
        message += " " + opt_arg
    package = fhm.text_message_encode(message)
    client_socket.sendall(package)
