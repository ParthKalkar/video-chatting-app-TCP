from os import environ
import requests
from receive_video import *
from receive_audio import *
from audio_server import *
from video_server import *

# Call listening port is 12344
# Video streaming port is 12345
# Audio streaming port is 12346

# CURRENT TODOLIST
# todo make the global variables part of classes
# todo solve all warnings
# todo plan the structure of files
# todo review the compatibility and performance of the libraries used (opencv and pyaudio)
# todo fix the thread names and numbers

environ["QT_DEVICE_PIXEL_RATIO"] = "0"
environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
environ["QT_SCREEN_SCALE_FACTORS"] = "1"
environ["QT_SCALE_FACTOR"] = "1"


class InitiateCallThread(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self) -> None:
        print("You can either call someone or wait for someone to call you.")
        my_ip = get_my_private_ip()
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
        IP = ''
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
        # audio_server.start()

        # receive ip
        ip = connection.recv(1024)
        global correspondent_ip
        print(address)
        correspondent_ip = ip.decode('utf-8')
        print("Correspondent said their IP is " + correspondent_ip)
        # print("However their local IP is : ")

        # send my ip
        connection.sendall(bytes(get_my_private_ip(), 'utf-8'))

        # ACK
        msg = connection.recv(1024)
        print(f"From {address} : {msg.decode('utf-8')}")

        t1 = ReceiveFrameThread(1, "Receive frame", 1)
        t2 = DisplayFrameThread(2, "Display frame", 2)
        # t3 = ReceiveAudioFrameThread(3, 'Receive Audio', 3)
        # t4 = PlayAudioThread(4, "Play Audio", 4)

        t1.start()
        t2.start()
        # t3.start()
        # t4.start()

        t1.join()
        t2.join()
        # t3.join()
        # t4.join()
        video_server.join()
        # audio_server.join()
        print("Exiting the call listening thread.")


def get_my_public_ip():
    # return '85.26.165.173'
    # return '10.91.49.174'  # University student
    # return '10.241.1.187'  # Connecting to ethernet in my room

    r = requests.get(r'http://jsonip.com')
    ip = r.json()['ip']
    print('Your IP is', ip)
    return ip


def get_my_private_ip():
    # print(system('ifconfig'))
    # todo Understand what the following code does
    # todo Does this require Internet access to work?
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    res = s.getsockname()[0]
    s.close()
    return res


print("Welcome to the best video chat app in the world!")

print("Your private IP address : " + str(get_my_private_ip()))

choice = -1
while 1:
    # global choice
    choice = input("Do you wanna make a call? (y/n) : ")
    if choice == 'y' or choice == 'n':
        break
    else:
        print("Invalid input /!\\ please try again.")

if choice == 'n':
    t1 = CallListeningThread(30, "Listen for call", 30)
    t1.start()
    t1.join()
else:
    t2 = InitiateCallThread(30, "Make a call", 30)
    t2.start()
    t2.join()

print("Exiting main thread")
