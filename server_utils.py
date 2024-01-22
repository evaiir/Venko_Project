import os
import socket
import shutil

import communication_utils as commu

CHUNK_SIZE = 1024


def receive_request(client_socket: socket.socket) -> list:
    request = commu.receive_text(client_socket)
    return request.split()


def change_directory(file_path: str):
    if os.path.isdir(file_path):
        os.chdir(file_path)
    else:
        raise ValueError(f"The selected path is not a directory.")


def confirm_filetype_with_client(client_socket: socket.socket, file_path: str) -> bool:
    if os.path.isdir(file_path):
        commu.send_text(client_socket, "dir")
    else:
        commu.send_text(client_socket, "file")

    return commu.receive_text(client_socket) == "y"
