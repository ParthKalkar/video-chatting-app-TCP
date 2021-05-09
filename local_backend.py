import socket
import time
import threading

import redis
from database import *

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


def online_list_listener(r: redis.Redis):
    while True:
        r.set("online_list", get_online_users())
        time.sleep(0.05)


def backend_server_redis():
    r = redis.Redis()
    r.set("python_started", True)

    current_username = None
    online_list_listener_thread = threading.Thread(target=online_list_listener, args=(r,))
    while 1:
        # Check username
        username = r.get("username")
        if username != current_username:
            signup(username)
            # todo start the call listener here
            if not online_list_listener_thread.is_alive():
                online_list_listener_thread.start()

        # Check for making a call
        make_call = r.get("make_call")
        if make_call:
            r.get("correspondent_id")
            # todo start the call making thread (will check for use_video and use_audio)

        # todo check incoming call (maybe in the call listening thread)
        # todo

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


