import socket
import redis
import time


def control_server(r: redis.Redis):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    port = 12347
    s.bind(('', port))
    s.listen(1)

    connection, address = s.accept()

    while 1:
        msg = connection.recv(4096).decode('utf-8')
        if msg == "VIDEO ON":
            r.set("show_video", "TRUE")
        elif msg == "VIDEO OFF":
            r.set("show_video", "FALSE")
        elif msg == "AUDIO ON":
            r.set("show_audio", "TRUE")
        elif msg == "AUDIO OFF":
            r.set("show_audio", "FALSE")

        status = r.get("status")
        if status == "quit":
            break

        time.sleep(0.1)
    s.close()


def control_client(correspondent_ip, r: redis.Redis):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
    port = 12344
    s.connect((correspondent_ip, port))

    last_video_status = True
    last_audio_status = True
    while True:
        video_status = r.get("use_video") == "ON"
        audio_status = r.get("use_audio") == "ON"
        if last_video_status != video_status:
            if video_status:
                s.sendall(b"VIDEO ON")
            else:
                s.sendall(b"VIDEO OFF")
            last_video_status = video_status

        if last_audio_status != audio_status:
            if audio_status:
                s.sendall(b"AUDIO ON")
            else:
                s.sendall(b"AUDIO OFF")
            last_audio_status = audio_status

        status = r.get("status")
        if status == "quit":
            break

        time.sleep(0.05)

    s.close()
