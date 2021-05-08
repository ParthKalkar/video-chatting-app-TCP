import socket

'''
The backend_server runs in a separate process, and it communicates with:
- Electron: Using a socket
- Python processes: Using pipes

The Python processes are mainly:
- call maker
- call listener
- video server
- audio server
- video receiver
- audio receiver
'''


def backend_server():
    # Front end socket creation
    front_end = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
    front_end.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    port = 12000
    ip = socket.gethostbyname('localhost')
    front_end.bind((ip, port))

    front_end.listen(1)
    front_end_conn, address = front_end.accept()

    # This part is basically an FSA
    while True:
        front_end_conn.recv(1024)


