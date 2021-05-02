from root import *
import cv2
import time
import pickle
from datetime import datetime

video_buffer = b""
video_buffer_lock = threading.Lock()
frame_size = -1


# correspondent_ip = ""

class ReceiveFrameThread(threading.Thread):
    def __init__(self, threadID, name, counter, correspondent_ip):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.correspondent_ip = correspondent_ip

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
        port = 12345
        IP = self.correspondent_ip
        s.connect((IP, port))

        print('Connection established (video receiver).')

        size = s.recv(1024)

        global frame_size
        frame_size = int(size.decode('utf-8'))

        print('Frame size in bytes : ' + str(size))

        frame_count = 0
        while True:

            # This part is synchronized with the video server (every 25 frames)
            # todo consider that the latency is actually way bigger for a frame because it has many packets
            # todo fix the problem when the hosts don't have the same timezone
            if frame_count == 25*(int(math.ceil(frame_size/4096))):
                packet = s.recv(53)  # The size of datetime object is 53 bytes
                sending_time = pickle.loads(packet)
                delta = datetime.now() - sending_time
                latency = abs(delta.total_seconds())  # todo check that the negative values are not actually a problem
                frame_latency = latency * (frame_size / 4096)
                frame_count = 0
                print("Current packet latency : " + str(latency))
                print("Estimated video latency : " + str(frame_latency))

                s.sendall(pickle.dumps(latency))  # todo make sure this is the most efficient way to sync

            packet = s.recv(4096)
            if not packet:
                print("No packet received !!!! Exiting the video receiving thread.")
                break
            frame_count += 1
            video_buffer_lock.acquire()
            global video_buffer
            video_buffer += packet
            # print('Size of video_buffer received  : ' + str(len(video_buffer)))
            video_buffer_lock.release()
            time.sleep(0.01)
        print('Exiting video receiving thread.')
        s.close()


class DisplayFrameThread(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self) -> None:
        print("Displaying frame thread started")
        while 1:
            global video_buffer
            if len(video_buffer) == 0 or frame_size == -1 or len(video_buffer) < frame_size:
                time.sleep(0.05)
                continue

            # If there is more than 1 second of video in the buffer, skip it (assuming 25 fps)
            # todo see if this is actually useful, because the buffer itself is not the bottleneck
            if len(video_buffer) > frame_size * 25:
                video_buffer_lock.acquire()
                video_buffer = b""
                video_buffer_lock.release()
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
        print("Exiting video playing thread.")
