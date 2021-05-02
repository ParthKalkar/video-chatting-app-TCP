from root import *
import time
import cv2
import pickle
from datetime import datetime


class SendFrameThread(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
        port = 12345
        IP = ''
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

        frame_count = 0

        while True:
            if frame_count == 25:
                connection.sendall(pickle.dumps(datetime.now()))
                frame_count = 0
                continue
            ret, frame = cap.read()
            if not ret:
                print("ERROR : couldn't read from webcam ! (Unknown reason)")
                break
            frame = pickle.dumps(frame)
            frame_count += 1
            connection.sendall(frame)
            # print("Frame sent. (size=" + str(len(frame)) + ")")
            time.sleep(0.01)

        s.close()
        print('Exiting video server.')
