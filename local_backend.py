import socket
import time

import redis

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


def backend_server_redis():
    r = redis.Redis()
    r.set("python_started", True)
    while 1:

        # Need to implement a good protocol here, will probably be easier then sockets

        close = r.get("quit")
        if close:
            break

        # Sleep between polls
        time.sleep(0.001)


def backend_server_socket():
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


