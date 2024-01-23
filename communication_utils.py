import os
import socket
import tarfile
import time

import file_utils as f_utils

CHUNK_SIZE = 1024
INT_SIZE = 4


def send_text(client_socket: socket.socket, message: str):
    """
    Sends a string text to the receiver.
    The text will actually be sent as message size + encoded message concatenated.
    """
    package = f_utils.text_message_encode(message)

    # Send the actual message
    client_socket.sendall(package)


def receive_text(client_socket: socket.socket) -> str:
    """Receives an encoded message from the sender and returns the decoded text as a string."""
    length_bytes = client_socket.recv(INT_SIZE)
    length = int.from_bytes(length_bytes)

    message = b""
    while length:
        package = client_socket.recv(min(CHUNK_SIZE, length))
        message += package
        length -= len(package)

    return message.decode("utf-8")


def send_file(client_socket: socket.socket, file_path: str):
    """
    Send a file to the other side of the connection.

    If the selected file is a directory, the function will compress the directory into a .tar.gz
    temp file and send it instead. The temp file is removed after the file is sent.

    The file is sent along a JSON containing the file's metadata. The package is sent to the
    receiver as the length of the JSON + the JSON + file binary concatenated.
    """
    file_path = os.path.expanduser(file_path)
    file_compressed = False
    if os.path.isdir(file_path):
        with tarfile.open(file_path + ".tar.gz", "w:gz") as tar:
            tar.add(file_path, arcname=os.path.basename(file_path))
        file_path += ".tar.gz"
        file_compressed = True

    encoded_file = f_utils.file_encode(file_path, file_compressed)

    # Send file content in small chunks of size CHUNK_SIZE
    for i in range(0, len(encoded_file), CHUNK_SIZE):
        package = encoded_file[i : i + CHUNK_SIZE]
        client_socket.send(package)

    # Delete the compressed temp file and adjust the file_path name.
    if file_compressed:
        f_utils.delete_file(file_path)
        file_path = file_path[:-7]  # Removes the ".tar.gz" from the name
        timestamped_print(f"Directory '{file_path}' sent successfully.")
    else:
        timestamped_print(f"File '{file_path}' sent successfully.")


def receive_file(client_socket: socket.socket, file_path: str | None):
    """
    Receive a file from the other side of the connection.

    If the file to be received was supposed to be a directory, a temp compressed .tar.gz will
    be received instead. The function will handle the decompression and then delete the temp file.
    """
    metadata = f_utils.get_file_metadata(client_socket)

    file_path = os.path.expanduser(file_path or ".")
    file_name = metadata["file_name"]
    full_name = os.path.join(file_path, file_name)

    length = metadata["file_len"]

    try:
        with open(full_name, "wb") as file:
            while length:
                package = client_socket.recv(min(CHUNK_SIZE, length))
                file.write(package)
                length -= len(package)
    except PermissionError:
        raise PermissionError(
            f"You don't have permission to create/write on {file_name}."
        )

    os.chmod(file_name, metadata["permissions"])  # Restore received file permissions.
    if metadata["is_compressed"]:
        with tarfile.open(file_name, "r:gz") as tar:
            tar.extractall(os.curdir)
        f_utils.delete_file(file_name)
        file_name = file_name[:-7]  # Remove the ".tar.gz" from the name.
        timestamped_print(f"Directory '{file_name}' received successfully.")
    else:
        timestamped_print(f"File '{file_name}' received successfully.")


def timestamped_print(message: str):
    """
    Concatenate a timestamp before the string to be printed.

    The timestamp uses the format [yy-mm-dd h:min:s]
    """
    t = time.time()
    timestamp = "[" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t)) + "]"
    timestamped_message = timestamp + " - " + message
    print(timestamped_message)
