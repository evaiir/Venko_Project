# Multiclient Socket Server

This project was developed as part of the internship application to Venko
Networks. It is a simple multiclient socket server written in Python 3.11,
utilizing only standard Python libraries. Therefore, no external dependencies
are required. The available commands for clients include listing, downloading,
and deleting files from the server, as well as uploading files to the server.
All actions are performed within the terminal.

## Communication protocol

The program uses two different communication methods:

1. Text message communication:
- First, the sender encodes the text message being sent.
- The sender forms a package concatenating the size of the encoded message with
  the encoded text.
- The package is sent to the receiver.
- On the receiver side, the program reads the first 4 bytes to get the size of
  the incoming package.
- The receiver uses that information to know when to stop receiving data from
  the socket.
2. File exchange communication:
- First, the sender checks if the file to be sent is actually a directory.
- In that case, the directory will be compressed into a tarball (.tar.gz file)
- The sender then stores metadata from the file into a dictionary.
- The dict contains these informations:
    - If the file was compressed
    - Filename
    - File length
    - File permissions
- The dictionary is then transformed into a JSON and encoded.
- The sender forms a package concatenating the size of the encoded JSON with the
  encoded JSON and the filedata.
- The package is sent.
- If the package contained a compressed directory, the aditional tarball file
  created on the sender side is now deleted.
- On the receiver side, the program reads the first 4 bytes to get the size of
  the JSON
- The JSON is translated back to a dictionary and the receiver collects the metadata
  from the file.
- The receiver uses the file length to know when to stop receiving data from the
  socket.
- If it was a directory, the tarball that was received is decompressed and the
  compressed version received is deleted.

When the client asks the server to download or delete a file, they first request
the action, specifying the file on which the operation should be performed. The
server responds by indicating the type of the file—whether it's a normal file, a
directory, or if the file doesn't exist.
After receiving this information, the client is presented with a prompt asking
for confirmation of the action. The prompt also warns the client if the action
will affect a directory. The upload command follows a similar process of
information exchange, but the file type checking occurs locally on the
client side.
