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
    r.set("status", "waiting_username")
    r.set("use_video", "TRUE")
    r.set("use_audio", "TRUE")
    r.set("online_list", "")
    r.set("incoming_status", "waiting_username")
    r.set("outgoing_status", "waiting_username")
    r.set("username", "")
    r.set("correspondent_id", "")
    r.set("correspondent_ip", "")
    r.set("correspondent_name", "")
    r.set("current_video_frame", "")
    r.set("python_status", "ON")

    current_username = None
    online_list_listener_thread = threading.Thread(target=online_list_listener, args=(r,))
    while 1:
        # Check status first
        status = r.get("status")
        if status == "waiting_username":
            # Check username
            username = r.get("username")
            if username != current_username:
                signup(username)
                go_online(username, get_my_private_ip())
                current_username = username
                # todo start the call listener here
                if not online_list_listener_thread.is_alive():
                    online_list_listener_thread.start()

            r.set("status", "home")
        elif status == "home":
            print("jkm")
            # todo check if I need to do anything here (maybe reset vars after a call)
        elif status == "incoming":
            incoming_status = r.get("incoming_status")
            if incoming_status == "declined":
                r.set("status", "home")
            elif incoming_status == "accepted":
                r.set("status", "call")
        elif status == "calling":
            id = r.get("correspondent_id")
            # todo start the call making thread

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



