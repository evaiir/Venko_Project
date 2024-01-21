import os
import socket

import file_handling_module as fhm


def receive_request(client_socket: socket.socket) -> list:
    request = receive_text(client_socket)
    return request.split()


# Wrapper to handle text communication through the network
def send_text(client_socket: socket.socket, message: str):
    package = fhm.text_message_encode(message)

    # Send the actual message
    client_socket.sendall(package)


def receive_text(client_socket: socket.socket) -> str:
    length_bytes = client_socket.recv(4)
    length = int.from_bytes(length_bytes)

    message = b""
    while length:
        package = client_socket.recv(min(1024, length))
        message += package
        length -= len(package)

    return message.decode("utf-8")


def send_file(client_socket: socket.socket, file_path: str):
    file_path = os.path.expanduser(file_path)

    encoded_file = fhm.file_encode(file_path)

    # Send file content
    for i in range(0, len(encoded_file), 1024):
        package = encoded_file[i : i + 1024]
        client_socket.send(package)


def receive_file(client_socket: socket.socket, file_path: str | None):
    metadata = fhm.get_file_metadata(client_socket)

    file_path = os.path.expanduser(file_path or ".")
    file_name = metadata["file_name"]
    full_name = os.path.join(file_path, file_name)

    length = metadata["file_len"]

    try:
        file = open(full_name, "wb")
    except PermissionError:
        print(f"You don't have permission to read {file_name}.")
        return
    else:
        with file:
            while length:
                package = client_socket.recv(min(1024, length))
                file.write(package)
                length -= len(package)

    print(f"File '{file_name}' received successfully.")


def delete_file(file_path: str):
    file_path = os.path.expanduser(file_path)
    os.remove(file_path)


def change_directory(file_path: str):
    file_path = os.path.expanduser(file_path or "~/")
    os.chdir(file_path)
