import os
import socket
import tarfile
import time

import file_utils as f_utils

CHUNK_SIZE = 1024


# Wrapper to handle text communication through the network
def send_text(client_socket: socket.socket, message: str):
    package = f_utils.text_message_encode(message)

    # Send the actual message
    client_socket.sendall(package)


def receive_text(client_socket: socket.socket) -> str:
    length_bytes = client_socket.recv(4)
    length = int.from_bytes(length_bytes)

    message = b""
    while length:
        package = client_socket.recv(min(CHUNK_SIZE, length))
        message += package
        length -= len(package)

    return message.decode("utf-8")


def send_file(client_socket: socket.socket, file_path: str):
    file_path = os.path.expanduser(file_path)
    if os.path.isdir(file_path):
        with tarfile.open(file_path + ".tar.gz", "w:gz") as tar:
            tar.add(file_path, arcname=os.path.basename(file_path))
        file_path += ".tar.gz"

    encoded_file = f_utils.file_encode(file_path)

    # Send file content
    for i in range(0, len(encoded_file), CHUNK_SIZE):
        package = encoded_file[i : i + CHUNK_SIZE]
        client_socket.send(package)

    if file_path.endswith(".tar.gz"):
        f_utils.delete_file(file_path)
        file_path = file_path[:-7]  # Removes the ".tar.gz" from the name
        timestamped_print(f"Directory '{file_path}' sent successfully.")
    else:
        timestamped_print(f"File '{file_path}' sent successfully.")


def receive_file(client_socket: socket.socket, file_path: str | None):
    metadata = f_utils.get_file_metadata(client_socket)

    file_path = os.path.expanduser(file_path or ".")
    file_name = metadata["file_name"]
    full_name = os.path.join(file_path, file_name)

    length = metadata["file_len"]

    try:
        file = open(full_name, "wb")
    except PermissionError:
        raise PermissionError(f"You don't have permission to create/write on {file_name}.")
    else:
        with file:
            while length:
                package = client_socket.recv(min(CHUNK_SIZE, length))
                file.write(package)
                length -= len(package)

    os.chmod(file_name, metadata["permissions"])
    if file_name.endswith(".tar.gz"):
        with tarfile.open(file_name, "r:gz") as tar:
            tar.extractall(os.curdir)
        f_utils.delete_file(file_name)
        file_name = file_name[:-7]  # Removes the ".tar.gz" from the name
        timestamped_print(f"Directory '{file_name}' received successfully.")
    else:
        timestamped_print(f"File '{file_name}' received successfully.")


def timestamped_print(message: str) -> str:
    t = time.time()
    timestamp = "[" + time.strftime('%Y-%m-%d %H:%M', time.localtime(t)) + "]"
    timestamped_message = timestamp + " - " + message
    print(timestamped_message)
