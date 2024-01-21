import socket

import file_handling_module as fhm
import server_module as sm

# Server configuration.
host = str(socket.INADDR_ANY)  # Bind to any interface
port = 8080

# Create a socket object.
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to a specific address and port.
server_socket.bind((host, port))

# Listen for incoming connections (currently only one at a time).
server_socket.listen(1)
print(f"Server listening on any interface on port {port}")

# Accept a connection.
client_socket, client_address = server_socket.accept()
print(f"Connection from {client_address} accepted.")

# Run the server requests until client exits.
while True:
    requests = sm.receive_request(client_socket)
    request_type, arg1 = requests[:2] + [None] * (2 - len(requests))
    print(f"I got those arguments from the request: {requests}")

    match request_type:
        case "/list" | "/ls":
            dir_list = fhm.list_content(arg1)
            sm.send_text(client_socket, dir_list)
            print("I listed the directory normally.")
        case "/tree":
            tree_list = fhm.tree_list_content(arg1)
            sm.send_text(client_socket, tree_list)
            print("I listed the directory as a tree.")
        case "/exit":
            break
        case "/upload":
            sm.receive_file(client_socket, arg1)
            print("I received a file!")
        case "/download":
            sm.send_file(client_socket, arg1)
            print("I sent a file!")
        case "/delete":
            sm.delete_file(arg1)
            print(f"I deleted a file!")
        case "/cd":
            sm.change_directory(arg1)
            print("I changed to another directory")


# Close the connection
client_socket.close()
server_socket.close()
