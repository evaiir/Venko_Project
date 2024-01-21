import json
import socket
import os
from pathlib import Path
from typing import Dict

def tree_list_content(directory: str) -> str:
    directory = os.path.expanduser(directory or '.')

    # Tree function lightly adapted from https://stackoverflow.com/a/59109706
    # prefix components:
    space = "    "
    branch = "│   "
    # pointers:
    tee = "├── "
    last = "└── "
    def tree(dir_path: Path, prefix: str = ""):
        """
        A recursive generator, given a directory Path object
        will yield a visual tree structure line by line
        with each line prefixed by the same characters
        """

        contents = [path for path in dir_path.iterdir()]
        # contents each get pointers that are ├── with a final └── :
        pointers = [tee] * (len(contents) - 1) + [last]
        for pointer, path in zip(pointers, contents):
            yield prefix + pointer + path.name
            if path.is_dir():  # extend the prefix and recurse:
                extension = branch if pointer == tee else space
                # i.e. space because last, └── , above so no more |
                yield from tree(path, prefix=prefix + extension)

    string = str(Path(os.path.basename(directory))) + "\n"
    for line in tree(Path(directory)):
        string += line + "\n"

    return string


def list_content(directory: str) -> str:
    """
    Mimics the output of the 'ls' command from the terminal. Return it as a string.
    """
    directory = os.path.expanduser(directory or '.')
    string = ''
    for line in os.listdir(directory):
        string += line + "\n"
    return string


def file_encode(file_path: str) -> bytes:
    """
    Receives a file with full path and returns a binary containing the length of the file name, the file
    name, the length of the file and the file concatenated.
    """
    file_info = {}
    file_info["file_name"] = os.path.basename(file_path)
    file_info["permissions"] = os.stat(file_path).st_mode

    try:
        file = open(file_path, "rb")
    except PermissionError:
        print(f"You don't have permission to read {file_info['file_name']}.")
        raise
    else:
        with file:
            file_data = file.read()

    file_info["file_len"] = len(file_data)
    metadata_bytes = json.dumps(file_info).encode('utf-8')
    metadata_length_bytes = len(metadata_bytes).to_bytes(4)
    encoded_file = metadata_length_bytes + metadata_bytes + file_data

    return encoded_file


def get_file_metadata(client_socket: socket.socket) -> Dict:
    """
    Receives the file name and both length informations from the buffer and return them to the function,
    so the caller can handle the file binaries.
    """
    dict_len_b = client_socket.recv(4)
    dict_len = int.from_bytes(dict_len_b)
    print(f"DICT TESTE: {dict_len}")

    encoded_file = client_socket.recv(dict_len)
    print(encoded_file)
    file_metadata = json.loads(encoded_file)

    return file_metadata


def text_message_encode(message: str) -> bytes:
    """
    Receives a string and returns its length and the encoded string to the caller can handle sending
    text through the network.
    """
    message_bytes = message.encode("utf-8")
    text_len = len(message_bytes)

    binary_data = text_len.to_bytes(4)
    binary_data += message_bytes

    return binary_data
