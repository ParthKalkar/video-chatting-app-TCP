from root import *
import cv2
import time
import pickle
from datetime import datetime

video_buffer = b""
video_buffer_lock = threading.Lock()
frame_size = -1
tmp_frame_size = []  # to be used when the frame size is changed in the receiver thread but not in the display thread
tmp_frame_size_lock = threading.Lock()


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

        # todo add a latency check here

        size = s.recv(1024)

        global frame_size
        frame_size = int(size.decode('utf-8'))

        print('Video receiver : Frame size in bytes : ' + str(size))

        total_received_bytes = 0

        while True:
            global video_buffer
            packet = s.recv(4096)
            if not packet:
                print("Video receiver : No packet received !!!! Exiting the video receiving thread.")
                break

            print("Video receiver : Packet size " + str(len(packet)))

            total_received_bytes += len(packet)
            # This part is synchronized with the video server (every 25 frames)
            # todo consider that the latency is actually way bigger for a frame because it has many packets
            # todo fix the problem when the hosts don't have the same timezone

            # The size of datetime object is 53 bytes (we are assuming that the packet will be exactly that)
            # if len(packet_end) == 53 and type(pickle.loads(packet)) == datetime:  # todo check this condition
            print(total_received_bytes)
            if total_received_bytes > 25*frame_size:
                packet_end = packet[:-53]
                print("Video receiver : Received packet seems to be the server time.")
                sending_time = pickle.loads(packet_end)
                print("Video receiver : Received server time.")
                delta = datetime.now() - sending_time
                latency = abs(delta.total_seconds())  # todo check that the negative values are not actually a problem
                frame_latency = latency * (frame_size / 4096)
                print("Video receiver : Current packet latency : " + str(latency))
                print("Video receiver : Estimated video latency : " + str(frame_latency))

                s.sendall(pickle.dumps(latency))  # todo make sure this is the most efficient way to sync

                new_frame_size = s.recv(4096)  # todo make sure it will only receive the new frame size
                new_frame_size = int(new_frame_size.decode('utf-8'))
                print("Video receiver : Frame size changed by server to " + str(new_frame_size))
                # global tmp_frame_size
                # tmp_frame_size_lock.acquire()
                # tmp_frame_size.append(new_frame_size)  # tmp_frame_size now has the changes of frame size in order.
                # tmp_frame_size_lock.release()
                # buffer_string = "NEW_FRAME_SIZE"
                # # global video_buffer
                # video_buffer_lock.acquire()
                # video_buffer += pickle.dumps(buffer_string)
                # video_buffer_lock.release()

                s.sendall(b"OK")  # Send ACK
                total_received_bytes = 0
                # continue
                packet = packet[-53:]

            video_buffer_lock.acquire()
            video_buffer += packet
            video_buffer_lock.release()
            time.sleep(0.01)
        print('Video receiver : Exiting video receiving thread.')
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
            global frame_size
            # if len(video_buffer) < len(pickle.dumps("NEW_FRAME_SIZE")):
            #     continue
            # video_buffer_lock.acquire()
            # start = pickle.loads(video_buffer[:len(pickle.dumps("NEW_FRAME_SIZE"))])
            # video_buffer_lock.release()   # todo check that I don't need a lock here
            # if start == "NEW_FRAME_SIZE":
            #     print("Changing frame size.")
            #     video_buffer_lock.acquire()
            #     video_buffer = video_buffer[len(pickle.dumps("NEW_FRAME_SIZE")):]
            #     video_buffer_lock.release()
            #     global frame_size
            #     global tmp_frame_size  # todo check if I need a lock here
            #     tmp_frame_size_lock.acquire()
            #     frame_size = tmp_frame_size[0]
            #     tmp_frame_size = tmp_frame_size[1:]
            #     tmp_frame_size_lock.release()

            if len(video_buffer) == 0 or frame_size == -1 or len(video_buffer) < frame_size:
                time.sleep(0.05)
                continue

            # If there is more than 1 second of video in the buffer, skip it (assuming 25 fps)
            # todo see if this is actually useful, because the buffer itself is not the bottleneck
            if len(video_buffer) > frame_size * 25:
                video_buffer_lock.acquire()
                video_buffer = b""
                print("Video player : Too many frames in the buffer, clearing buffer.")
                video_buffer_lock.release()
                continue

            video_buffer_lock.acquire()
            next_frame = video_buffer[:frame_size]
            video_buffer = video_buffer[frame_size:]
            video_buffer_lock.release()
            frame = pickle.loads(next_frame)
            cv2.namedWindow('frame', cv2.WND_PROP_FULLSCREEN)
            cv2.imshow('frame', frame)
            cv2.waitKey(1)
        print("Exiting video playing thread.")
