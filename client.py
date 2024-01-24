import socket
import os

import client_utils as cl_utils
import communication_utils as comm_utils

dtprint = comm_utils.timestamped_print

# Server configuration
host = "192.168.1.4"
port = 8080

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
client_socket.connect((host, port))

# Greet
dtprint(f"Connected to {host}:{port}")
print("Type /help to list the available operations.")

# Send requests to the server until operation /exit is called.
while True:
    try:
        # Empty (optional) args are handled inside each function
        commands = input("New command: ").split()
        command_type, arg1, arg2, *_ = commands + [None] * 2

        match command_type:
            case "/help":
                cl_utils.print_help()


            case "/exit":
                cl_utils.send_request(client_socket, command_type, None)
                if cl_utils.validate_command(client_socket, command_type, None):
                    break


            case "/list" | "/ls" | "/tree":
                dtprint("Requesting file list from the server")
                cl_utils.send_request(client_socket, command_type, arg1)

                list_state = comm_utils.receive_text(client_socket)
                if list_state.endswith("Error"):
                    if list_state.startswith("FILE"):
                        ve = comm_utils.receive_text(client_socket)
                        raise FileNotFoundError(ve)
                    elif list_state.startswith("OS"):
                        raise OSError

                file_list = comm_utils.receive_text(client_socket)

                dtprint("File list received.")
                dtprint(f"Listing {arg1 if arg1 else '.'}")
                print(file_list)


            case "/upload":
                if arg1:
                    full_path = os.path.abspath(os.path.expanduser(arg1))
                    dtprint("Requesting an upload to the server.")
                    cl_utils.send_request(client_socket, command_type, arg2)
                    if cl_utils.validate_command(client_socket, command_type, full_path):
                        dtprint("Sending a file to the server.")
                        comm_utils.send_file(client_socket, full_path)
                else:
                    cl_utils.send_request(client_socket, "missarg", None)
                    dtprint("Error: No file specified to be uploaded.")


            case "/download":
                if arg1:
                    dtprint("Requesting a download to the server.")
                    cl_utils.send_request(client_socket, command_type, arg1)
                    if cl_utils.validate_command(client_socket, command_type, arg1):
                        dtprint("Receiving a file from the server.")
                        comm_utils.receive_file(client_socket, arg2)
                else:
                    cl_utils.send_request(client_socket, "missarg", None)
                    dtprint("Error: No file specified to be downloaded.")


            case "/delete":
                if arg1:
                    dtprint("Requesting a deletion to the server.")
                    cl_utils.send_request(client_socket, command_type, arg1)
                    if cl_utils.validate_command(client_socket, command_type, arg1):
                        feedback = comm_utils.receive_text(client_socket)
                        dtprint(feedback)
                else:
                    cl_utils.send_request(client_socket, "missarg", None)
                    dtprint("Error: No file specified to be deleted.")


            case None:
                dtprint("Error: Empty command.")


            case _:
                dtprint("Error: Unknown command. Type /help to see available commands.")


    except ValueError as ve:
        dtprint(f"{ve}")
    except PermissionError as pe:
        dtprint(f"{pe}")
    except FileNotFoundError as fe:
        dtprint(f"{fe}")
    except KeyboardInterrupt:
        print()
        dtprint("KeyboardInterrupt detected.")
        cl_utils.send_request(client_socket, "/exit", None)
        if cl_utils.validate_command(client_socket, "/exit", None):
            break
    except OSError:
        oe = comm_utils.receive_text(client_socket)
        dtprint(oe)


# Close the connection
client_socket.close()
