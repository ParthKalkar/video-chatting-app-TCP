from root import *
import cv2
import time
import pickle


video_buffer = b""
video_buffer_lock = threading.Lock()
frame_size = -1
correspondent_ip = ""

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
                time.sleep(0.01)
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
                time.sleep(0.01)
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
