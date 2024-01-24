import socket
import threading

import communication_utils as comm_utils
import server_utils as sv_utils

dtprint = comm_utils.timestamped_print

MAX_CLIENTS = 5

dtprint(f"Booting up the server. To exit from server press CTRL+C on the keyboard.")
# Server configuration.
host = socket.gethostbyname(socket.gethostname())
port = 8080

# Create a socket object. The server_socket is specified as a stream socket with IPv4
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to a specific address and port.
server_socket.bind((host, port))

# Listen for incoming connections.
server_socket.listen(MAX_CLIENTS)
dtprint(f"Server listening on ip {host} and port {port}")

threads = []
try:
    while True:
        connected_clients = len(threads)
        print(f"QTD CLIENT: {connected_clients}")
        if connected_clients < MAX_CLIENTS:
            # Accept a connection.
            client_socket, client_address = server_socket.accept()

            # Create a new thread to handle the client
            client_thread = threading.Thread(
                target=sv_utils.handle_client, args=(client_socket, client_address)
            )
            client_thread.start()
            threads.append(client_thread)

            # Remove finished threads
            threads = [thread for thread in threads if thread.is_alive()]
        else:
            # Briefly accepts the connection.
            client_socket, client_address = server_socket.accept()
            dtprint(f"Connection refused from client {client_address} due to max capacity.")
            warn = "Connection rejected: Server is at full capacity."
            comm_utils.send_text(client_socket, warn)
            client_socket.close()

except KeyboardInterrupt:
    print()
    dtprint(
        "Server shutting down sequence started. Waiting for active clients to finish."
    )
    for thread in threads:
        thread.join()

dtprint("All clients have finished. Shutting down the server now.")
server_socket.close()
