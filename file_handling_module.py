"""
TODO:
    - enhance the file and text structure to send them in a more organized form.
"""


import os
from pathlib import Path

def tree_list_content(directory):
    directory = os.path.expanduser(directory or '.')

    """
    Tree function lightly adapted from https://stackoverflow.com/a/59109706
    """
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


# Mimics the output of the 'ls' command from the terminal. Return it as a string.
def list_content(directory):
    directory = os.path.expanduser(directory or '.')
    string = ''
    for line in os.listdir(directory):
        string += line + "\n"
    return string


"""
Receives a file with full path and returns a binary containing the length of the file name, the file
name, the length of the file and the file concatenated.
"""
def file_encode(file_path):
    file_name = os.path.basename(file_path)
    name_len = len(file_name)

    binary = name_len.to_bytes(4)
    binary += file_name.encode("utf-8")

    with open(file_path, "rb") as file:
        file_binary = file.read()

    file_len = len(file_binary)

    binary += file_len.to_bytes(4)
    binary += file_binary

    return binary


"""
Receives the file name and both length informations from the buffer and return them to the function,
so the caller can handle the file binaries.
"""
def get_file_metadata(client_socket):
    name_len_b = client_socket.recv(4)
    name_len = int.from_bytes(name_len_b)

    file_name_b = client_socket.recv(name_len)
    file_name = file_name_b.decode("utf-8")

    file_len_b = client_socket.recv(4)
    file_length = int.from_bytes(file_len_b)

    return file_name, file_length


"""
Receives a string and returns its length and the encoded string to the caller can handle sending
text through the network.
"""
def text_encode(message):
    message = message.encode("utf-8")
    text_len = len(message)

    binary = text_len.to_bytes(4)
    binary += message

    return binary
