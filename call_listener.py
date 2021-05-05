from receive_video import *
from receive_audio import *
from audio_server import *
from video_server import *


class CallListeningThread(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self) -> None:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
        port = 12344
        IP = ''
        s.bind((IP, port))
        s.listen(10)
        print("Listening for incoming calls.")
        connection, address = s.accept()

        msg = connection.recv(1024).decode('utf-8')
        print(f"From {address} : {msg}")
        use_audio = 1
        if "NO AUDIO" in msg:
            use_audio = 0
        connection.sendall(b"OK")

        # Start my own video and audio servers
        video_server = SendFrameThread(10, "Send Video", 10)
        audio_server = SendAudioFrameThread(11, "Send Video", 11)

        video_server.start()
        if use_audio:
            print("Call listener : AUDIO ENABLED.")
            audio_server.start()

        # receive ip
        ip = connection.recv(1024)
        # global correspondent_ip
        print(address)
        correspondent_ip = ip.decode('utf-8')
        print("Correspondent said their IP is " + correspondent_ip)
        # print("However their local IP is : ")

        # send my ip
        connection.sendall(bytes(get_my_private_ip(), 'utf-8'))

        # ACK
        msg = connection.recv(1024)
        print(f"From {address} : {msg.decode('utf-8')}")

        t1 = ReceiveFrameThread(1, "Receive frame", 1, correspondent_ip)
        t2 = DisplayFrameThread(2, "Display frame", 2)
        t3 = ReceiveAudioFrameThread(3, 'Receive Audio', 3, correspondent_ip)
        t4 = PlayAudioThread(4, "Play Audio", 4)

        t1.start()
        t2.start()

        if use_audio:
            t3.start()
            t4.start()
            t3.join()
            t4.join()
            audio_server.join()

        t1.join()
        t2.join()
        video_server.join()
        print("Exiting the call listening thread.")
