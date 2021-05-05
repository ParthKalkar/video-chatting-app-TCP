from receive_video import *
from receive_audio import *
from audio_server import *
from video_server import *
from database import *


class InitiateCallThread(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self) -> None:
        my_ip = get_my_private_ip()
        online_users = get_online_users()
        print("You can call someone either by choosing their number in the list below")
        if online_users is None:
            print("Looks like no one is online right now, go and talk to people IRL instead.")
            return

        online_users = list(online_users)
        for i in range(len(online_users)):
            print(str(i+1) + " - " + str(online_users[i]['name']))

        index = int(input("Enter the number of the user you wanna call : "))

        ip = online_users[index-1]['ip']

        print("Initiating a call with " + ip)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
        port = 12344
        s.connect((ip, port))

        print('Connection established to make the call.')

        choice = -1
        while 1:
            choice = input("Do you wanna use audio during the call? (y/n) : ")
            if choice == 'y' or choice == 'n':
                break
            else:
                print("Invalid input /!\\ Try again please.")

        use_audio = (0, 1)[choice == 'y']
        s.sendall((b"Call", b"Call NO AUDIO")[not use_audio])

        msg = s.recv(1024)
        print('Your correspondent said : ' + msg.decode('utf-8'))

        s.sendall(bytes(my_ip, 'utf-8'))

        video_server = SendFrameThread(10, "Send Video", 10)
        video_server.start()

        audio_server = SendAudioFrameThread(11, "Send Video", 11)

        if use_audio:
            print("Starting audio server.")
            audio_server.start()

        msg = s.recv(1024)
        print('Your correspondent gave back their IP : ' + msg.decode('utf-8'))
        correspondent_ip = msg.decode('utf-8')

        s.sendall(b"OK")

        t1 = ReceiveFrameThread(1, "Receive frame", 1, correspondent_ip)
        t2 = DisplayFrameThread(2, "Display frame", 2)
        t3 = ReceiveAudioFrameThread(3, 'Receive Audio', 3, correspondent_ip)
        t4 = PlayAudioThread(4, "Play Audio", 4)

        t1.start()
        t2.start()
        t1.join()
        t2.join()
        video_server.join()

        if use_audio:
            print("Starting other audio threads.")
            t3.start()
            t4.start()
            t3.join()
            t4.join()
            audio_server.join()

        print("Exiting the call making thread.")