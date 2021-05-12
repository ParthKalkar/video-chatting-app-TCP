import socket
import time
import threading

import redis
from database import *
import json
from call_maker import *
from call_listener import *
import multiprocessing

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


def start_call_maker(ip, r):
    main_thread = InitiateCallThread(1, "call maker", 1, ip, r)
    main_thread.start()
    main_thread.join()
    print("Ended the call making process.")


def start_call_listener(r):
    main_thread = CallListeningThread(1, "call listener", 1, r)
    main_thread.start()
    main_thread.join()
    print("Ended the call listening process.")


def online_list_listener(r: redis.Redis):
    print("Online list listener started.")
    while True:
        status = r.get("status").decode("utf-8")
        if status == 'quit':
            r.set("online_list", "[]")
            break
        if status != 'home':
            time.sleep(0.5)
            continue

        online_list = get_online_users()
        res = []
        count = 0
        for i in online_list:
            entry = {
                'id': count,
                'name': i['name'],
                'ip': i['ip']
            }
            res.append(entry)
            count += 1
        # print(res)
        r.set("online_list", json.dumps(res))
        time.sleep(0.2)


def backend_server_redis():
    r = redis.Redis()
    r.set("status", "waiting_username")
    r.set("use_video", "TRUE")
    r.set("use_audio", "TRUE")
    r.set("show_video", "TRUE")
    r.set("show_audio", "TRUE")
    r.set("online_list", "[]")
    r.set("incoming_status", "waiting_username")
    r.set("outgoing_status", "waiting_username")
    r.set("username", "")
    r.set("correspondent_id", "")
    r.set("correspondent_ip", "")
    r.set("correspondent_name", "")
    r.set("current_video_frame", "")
    r.set("python_status", "ON")
    r.set("own_webcam", "")
    r.set("other_webcam", "")

    current_username = ""
    online_list_listener_thread = threading.Thread(target=online_list_listener, args=(r,))

    while 1:
        # Check status first
        status = r.get("status").decode('utf-8')
        if status == "waiting_username":
            # Check username
            username = r.get("username").decode('utf-8')
            if username != current_username:
                print(f'Username in Python: {username}')
                signup(username)
                go_online(username, get_my_private_ip())
                current_username = username
                # todo start the call listener here
                call_listener_process = multiprocessing.Process(target=start_call_listener, args=(r,))
                call_listener_process.start()
                print("Started the call listener process.")
                if not online_list_listener_thread.is_alive():
                    online_list_listener_thread.start()

                r.set("status", "home")
        elif status == "home":
            continue
            # todo check if I need to do anything here (maybe reset vars after a call)

        elif status == "incoming":

            ip = r.get("correspondent_ip")
            if ip != "":
                name = get_username_by_ip(ip)
                r.set("correspondent_name", name)

            incoming_status = r.get("incoming_status")
            if incoming_status == "declined":
                # We should restart the call listener because it quits when we decline.
                call_listener_process = multiprocessing.Process(target=start_call_listener, args=(r,))
                call_listener_process.start()
                print("Started the call listener process.")
                r.set("status", "home")
            elif incoming_status == "accepted":
                r.set("status", "call")

        elif status == "initiate_call":
            i = int(r.get("correspondent_id").decode('utf-8'))
            online_users = list(get_online_users())
            ip = online_users[i]['ip']
            name = online_users[i]['name']
            r.set("correspondent_ip", ip)
            r.set("correspondent_name", name)

            # todo start the call making thread
            call_maker_process = multiprocessing.Process(target=start_call_maker, args=(ip, r,))
            go_offline(current_username)
            call_maker_process.start()
            print("Started the call maker process.")
            r.set("status", "calling")
            r.set("calling_status", "ringing")

        elif status == "calling":
            calling_status = r.get("calling_status").decode("utf-8")
            if calling_status == "ringing":
                continue
            elif calling_status in ["line_busy", "cancelled", "declined", "error"]:
                go_online(current_username, get_my_private_ip())
                r.set("status", "home")
            elif calling_status == "accepted":
                r.set("status", 'call')
            else:
                print("ERROR: Unexpected calling status.")

        # Check for making a call
        make_call = r.get("make_call")
        if make_call:
            r.get("correspondent_id")
            # todo start the call making thread (will check for use_video and use_audio)

        # todo check incoming call (maybe in the call listening thread)
        # todo

        status = r.get("status").decode('utf-8')
        # print(status)
        if status == 'quit':
            go_offline(current_username)
            kill_listener()
            break

        # Sleep between polls
        time.sleep(0.1)
