from root import *
import time
import cv2
import pickle

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
            time.sleep(0.01)

        print('Connection terminated !')
        s.close()

