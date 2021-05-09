from root import *
import cv2
import time
import pickle
from datetime import datetime
import redis

video_buffer = [b""]
video_buffer_lock = []
frame_size = [-1]
frame_size_lock = []
tmp_frame_size = [[]]  # to be used when the frame size is changed in the receiver thread but not in the display thread
tmp_frame_size_lock = []

parallel_connections = 20

buffer_ready = False


def init_locks_and_buffers(number_of_connections):
    global video_buffer, video_buffer_lock, frame_size, frame_size_lock, tmp_frame_size, tmp_frame_size_lock

    video_buffer = []
    frame_size = []
    tmp_frame_size = []

    video_buffer_lock = []
    frame_size_lock = []
    tmp_frame_size_lock = []

    for i in range(number_of_connections):
        video_buffer.append(b"")
        frame_size.append(-1)
        tmp_frame_size.append([])

        video_buffer_lock.append(threading.Lock())
        frame_size_lock.append(threading.Lock())
        tmp_frame_size_lock.append(threading.Lock())
    global buffer_ready
    buffer_ready = True


def new_connection(ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
    port = 12345
    s.connect((ip, port))
    return s


def receive_frames(s, connection_id):
    size = s.recv(1024)

    global frame_size
    frame_size[connection_id] = int(size.decode('utf-8'))

    print('Video receiver : Frame size in bytes : ' + str(frame_size[connection_id]))

    total_received_bytes = 0

    while True:
        global video_buffer
        packet = s.recv(4096)
        if not packet:
            print("Video receiver : No packet received !!!! Exiting the child video receiving thread.")
            break

        total_received_bytes += len(packet)
        # This part is synchronized with the video server (every 25 frames)
        # todo consider that the latency is actually way bigger for a frame because it has many packets
        # todo fix the problem when the hosts don't have the same timezone

        # todo what if this is exactly the size of 25 frames?
        if total_received_bytes > 25 * frame_size[connection_id]:
            packet_end = packet[len(packet) - 53:]
            # print("Video receiver : Received packet seems to be the server time.")
            # print("Video receiver : Datetime packet length : " + str(len(packet_end)))
            sending_time = pickle.loads(packet_end)
            # print("Video receiver : Received server time.")
            delta = datetime.now() - sending_time
            latency = abs(delta.total_seconds())  # todo check that the negative values are not actually a problem
            # frame_latency = latency * (frame_size[connection_id] / 4096)
            # print("Video receiver : Current packet latency : " + str(latency))
            # print("Video receiver : Estimated video latency : " + str(frame_latency))

            s.sendall(pickle.dumps(latency))  # todo make sure this is the most efficient way to sync

            new_frame_size = s.recv(4096)  # todo make sure it will only receive the new frame size
            new_frame_size = int(new_frame_size.decode('utf-8'))
            # print("Video receiver : Frame size changed by server to " + str(new_frame_size))
            global tmp_frame_size
            tmp_frame_size_lock[connection_id].acquire()
            tmp_frame_size[connection_id].append(new_frame_size)  # tmp_frame_size now has the changes of frame size in order.
            tmp_frame_size_lock[connection_id].release()
            buffer_string = "NEW_FRAME_SIZE"
            packet = packet[:len(packet) - 53]
            video_buffer_lock[connection_id].acquire()
            video_buffer[connection_id] += packet
            video_buffer[connection_id] += bytes(buffer_string, 'utf-8')
            video_buffer_lock[connection_id].release()

            total_received_bytes = 0
            s.sendall(b"OK")  # Send ACK
            time.sleep(0.001)
            continue

        video_buffer_lock[connection_id].acquire()
        try:
            video_buffer[connection_id] += packet
        except IndexError as e:
            print("Exception" + str(e))
            print("ID : " + str(connection_id))
            print("Video buffer size : " + str(len(video_buffer)))

        video_buffer_lock[connection_id].release()
        time.sleep(0.001)
    print('Video receiver : Exiting child video receiving thread.')
    s.close()


class ReceiveFrameThread(threading.Thread):
    def __init__(self, thread_id, name, counter, correspondent_ip):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.name = name
        self.counter = counter
        self.correspondent_ip = correspondent_ip

    def run(self):
        init_locks_and_buffers(parallel_connections)
        print("After buffer init : \n")
        print(video_buffer)
        connection_threads = []
        for i in range(parallel_connections):
            s = new_connection(self.correspondent_ip)
            new_thread = threading.Thread(target=receive_frames, args=(s, i,))
            new_thread.start()
            print("Video receiver : Child thread started.")
            connection_threads.append(new_thread)

        # Join the threads
        for th in connection_threads:
            th.join()

        print("Exiting the main video receiver thread.")


class DisplayFrameThread(threading.Thread):
    def __init__(self, thread_id, name, counter, r: redis.Redis):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.name = name
        self.counter = counter
        self.r = r

    def run(self) -> None:
        print("Displaying frame thread started")

        # This is to make sure buffers are initialized before reading frames
        while not buffer_ready:
            time.sleep(0.05)

        while 1:
            status = self.r.get("status").decode('utf-8')
            if status == "quit":
                break

            show_video = self.r.get("show_video").decode("utf-8")
            if show_video == "FALSE":
                # todo make this display a profile image
                continue
            for i in range(parallel_connections):
                global video_buffer
                global frame_size
                if len(video_buffer[i]) < len(bytes("NEW_FRAME_SIZE", 'utf-8')):
                    continue
                video_buffer_lock[i].acquire()
                start = video_buffer[i][:len(bytes("NEW_FRAME_SIZE", 'utf-8'))]
                video_buffer_lock[i].release()

                valid_string = True
                try:
                    start = start.decode('utf-8')
                except UnicodeDecodeError:
                    valid_string = False

                if valid_string and start == "NEW_FRAME_SIZE":
                    # print("Video player : Changing frame size.")
                    video_buffer_lock[i].acquire()
                    video_buffer[i] = video_buffer[i][len(bytes("NEW_FRAME_SIZE", 'utf-8')):]
                    video_buffer_lock[i].release()
                    # global frame_size
                    global tmp_frame_size  # todo check if I need a lock here
                    tmp_frame_size_lock[i].acquire()
                    frame_size[i] = tmp_frame_size[i][0]
                    tmp_frame_size[i] = tmp_frame_size[i][1:]
                    tmp_frame_size_lock[i].release()
                    continue

                if len(video_buffer[i]) == 0 or frame_size[i] == -1 or len(video_buffer[i]) < frame_size[i]:
                    time.sleep(0.001)
                    continue

                # If there is more than 1 second of video in the buffer, skip it (assuming 25 fps)
                # todo see if this is actually useful, because the buffer itself is not the bottleneck
                if len(video_buffer[i]) > frame_size[i] * 25:
                    video_buffer_lock[i].acquire()
                    video_buffer[i] = b""
                    print("Video player : Too many frames in the buffer, clearing buffer.")
                    video_buffer_lock[i].release()
                    continue

                video_buffer_lock[i].acquire()
                next_frame = video_buffer[i][:frame_size[i]]
                video_buffer[i] = video_buffer[i][frame_size[i]:]
                video_buffer_lock[i].release()

                frame = pickle.loads(next_frame)
                cv2.namedWindow('frame', cv2.WND_PROP_FULLSCREEN)
                cv2.imshow('frame', frame)
                cv2.waitKey(1)

        print("Exiting video playing thread.")
