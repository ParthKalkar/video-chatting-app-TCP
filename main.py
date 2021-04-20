import socket
import cv2
import pickle
from os import environ
import threading
import time
import pyaudio
import requests

# Call listening port is 12344
# Video streaming port is 12345
# Audio streaming port is 12346

environ["QT_DEVICE_PIXEL_RATIO"] = "0"
environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
environ["QT_SCREEN_SCALE_FACTORS"] = "1"
environ["QT_SCALE_FACTOR"] = "1"

video_buffer = b""
video_buffer_lock = threading.Lock()
frame_size = -1

audio_buffer = b""
audio_buffer_lock = threading.Lock()

correspondent_ip = ""


class SendAudioFrameThread(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self) -> None:
        CHUNK = 4096
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
        port = 12346
        IP = ''  # socket.gethostbyname(socket.gethostname())  # '192.168.0.105'
        print("Server IP : " + IP)
        s.bind((IP, port))
        s.listen(10)

        print('Socket for audio created and listening.')

        connection, address = s.accept()

        print('Connection for audio from ' + str(address))

        p = pyaudio.PyAudio()

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        stream.start_stream()

        while True:
            try:
                data = stream.read(CHUNK)
            except Exception as e:
                print(e)
                break
            connection.sendall(data)

        stream.stop_stream()
        stream.close()
        p.terminate()
        s.close()


class SendFrameThread(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
        port = 12345
        IP = ''  # socket.gethostbyname(socket.gethostname()) #'192.168.0.105'
        print("Server IP : " + IP)
        s.bind((IP, port))
        s.listen(10)

        print('Socket created and listening.')

        connection, address = s.accept()

        print('Connection from ' + str(address))

        cap = cv2.VideoCapture(0)

        print('Established webcam stream.')

        ret, frame = cap.read()

        frame = pickle.dumps(frame)

        size = len(frame)

        connection.sendall(bytes(str(size), 'utf-8'))

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = pickle.dumps(frame)
            connection.sendall(frame)
            # print("Frame sent. (size=" + str(len(frame)) + ")")
            time.sleep(0.005)

        print('Connection terminated !')
        s.close()


class InitiateCallThread(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self) -> None:
        print("You can either call someone or wait for someone to call you.")
        my_ip = get_my_public_ip()
        print("In case you want someone to call you, give them your IP : " + my_ip)
        ip = input("If you wanna call someone, just enter their IP address : ")

        print("Initiating a call with " + ip)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
        port = 12344
        s.connect((ip, port))

        print('Connection established to make the call.')
        s.sendall(b"Call")

        msg = s.recv(1024)
        print('Your correspondent said ' + msg.decode('utf-8'))

        s.sendall(bytes(my_ip, 'utf-8'))

        video_server = SendFrameThread(10, "Send Video", 10)
        audio_server = SendAudioFrameThread(11, "Send Video", 11)

        video_server.start()
        audio_server.start()

        msg = s.recv(1024)
        print('Your correspondent gave back their IP : ' + msg.decode('utf-8'))
        global correspondent_ip
        correspondent_ip = msg.decode('utf-8')

        s.sendall(b"OK")

        t1 = ReceiveFrameThread(1, "Receive frame", 1)
        t2 = DisplayFrameThread(2, "Display frame", 2)
        t3 = ReceiveAudioFrameThread(3, 'Receive Audio', 3)
        t4 = PlayAudioThread(4, "Play Audio", 4)

        t1.start()
        t2.start()
        t3.start()
        t4.start()

        t1.join()
        t2.join()
        t3.join()
        t4.join()
        video_server.join()
        audio_server.join()

        print("Exiting the call making thread.")


class CallListeningThread(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self) -> None:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
        port = 12344
        IP = ''  # socket.gethostbyname(socket.gethostname())  # '192.168.0.105'
        s.bind((IP, port))
        s.listen(10)
        print("Listening for incoming calls.")
        connection, address = s.accept()

        msg = connection.recv(1024)
        print(f"From {address} : {msg}")
        connection.sendall(b"OK")

        # Start my own video and audio servers
        video_server = SendFrameThread(10, "Send Video", 10)
        audio_server = SendAudioFrameThread(11, "Send Video", 11)

        video_server.start()
        audio_server.start()

        # receive ip
        ip = connection.recv(1024)
        global correspondent_ip
        correspondent_ip = ip.decode('utf-8')
        print("Correspondent said their IP is " + correspondent_ip)

        # send my ip
        connection.sendall(bytes(get_my_public_ip(), 'utf-8'))

        # ACK
        msg = connection.recv(1024)
        print(f"From {address} : {msg.decode('utf-8')}")

        t1 = ReceiveFrameThread(1, "Receive frame", 1)
        t2 = DisplayFrameThread(2, "Display frame", 2)
        t3 = ReceiveAudioFrameThread(3, 'Receive Audio', 3)
        t4 = PlayAudioThread(4, "Play Audio", 4)

        t1.start()
        t2.start()
        t3.start()
        t4.start()

        t1.join()
        t2.join()
        t3.join()
        t4.join()
        video_server.join()
        audio_server.join()
        print("Exiting the call listening thread.")


def get_my_public_ip():
    # return '127.0.0.1'
    r = requests.get(r'http://jsonip.com')
    ip = r.json()['ip']
    print('Your IP is', ip)
    return ip


class ReceiveAudioFrameThread(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self) -> None:
        """ for x in range(0, p.get_device_count()):
            info = p.get_device_info_by_index(x)
            print(info)"""
        CHUNK = 4096
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
        port = 12346
        IP = correspondent_ip
        s.connect((IP, port))

        print('Connection established for audio.')
        audio_data = s.recv(CHUNK)
        while audio_data != "":
            global audio_buffer
            try:
                audio_data = s.recv(CHUNK)
                audio_buffer_lock.acquire()
                audio_buffer += audio_data
                audio_buffer_lock.release()
            except socket.error:
                print("Server disconnected.")
                break


class PlayAudioThread(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self) -> None:
        CHUNK = 4096
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        p = pyaudio.PyAudio()  # todo fix the bug with this shit (only happens when not using localhost)
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        output=True,
                        frames_per_buffer=CHUNK)
        stream.start_stream()
        print("Audio device started.")
        while True:
            global audio_buffer
            if len(audio_buffer) >= CHUNK * 10:
                audio_buffer_lock.acquire()
                stream.write(audio_buffer[:CHUNK * 5])
                audio_buffer = audio_buffer[CHUNK * 5:]
                audio_buffer_lock.release()
        stream.stop_stream()
        stream.close()
        p.terminate()


class ReceiveFrameThread(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
        port = 12345
        IP = correspondent_ip
        s.connect((IP, port))

        print('Connection established.')

        size = s.recv(1024)

        global frame_size
        frame_size = int(size.decode('utf-8'))

        print('Frame size in bytes : ' + str(size))

        for i in range(100000000):
            while True:
                packet = s.recv(4096)
                if not packet:
                    print("No packet received !!!!")
                    break
                video_buffer_lock.acquire()
                global video_buffer
                video_buffer += packet
                # print('Size of video_buffer received  : ' + str(len(video_buffer)))
                video_buffer_lock.release()
        print('Connection terminated !')
        s.close()


class DisplayFrameThread(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self) -> None:
        print("displaying frame thread started")
        for i in range(1000000):
            global video_buffer
            if len(video_buffer) == 0 or frame_size == -1 or len(video_buffer) < frame_size:
                time.sleep(0.005)
                continue
            video_buffer_lock.acquire()
            nextframe = video_buffer[:frame_size]
            video_buffer = video_buffer[frame_size:]
            video_buffer_lock.release()
            # print(type(nextframe))
            # print(video_buffer)
            frame = pickle.loads(nextframe)
            # print(type(frame))
            cv2.namedWindow('frame', cv2.WND_PROP_FULLSCREEN)
            cv2.imshow('frame', frame)
            cv2.waitKey(1)


print("Welcome to the best video chat app in the world!")

'''t1 = ReceiveFrameThread(1, "Receive frame", 1)
t2 = DisplayFrameThread(2, "Display frame", 2)
t3 = ReceiveAudioFrameThread(3, 'Receive Audio', 3)
t4 = PlayAudioThread(4, "Play Audio", 4)

t1.start()
t2.start()
t3.start()
t4.start()

t1.join()
t2.join()
t3.join()
t4.join()'''

t1 = CallListeningThread(30,"Make a call", 30)
t2 = InitiateCallThread(31,"Init call", 31)

t1.start()
t2.start()

t1.join()
t2.join()

print("Exiting main thread")
