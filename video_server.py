from root import *
import time
import cv2
import pickle
from datetime import datetime

MAX_LATENCY = 0.09  # The maximum allowed latency in seconds


def resize_image(src, ratio):
    width = int(src.shape[1] * ratio)
    height = int(src.shape[0] * ratio)

    new_size = (width, height)

    # resize image
    return cv2.resize(src, new_size)


def video_stream(connection):
    # todo add the appropriate locks (for cap) (if using one cap object passed to function)
    scaling_ratio = 0.1
    cap = cv2.VideoCapture(0)
    print('Video server : Established webcam stream from child server thread.')
    # Initial frame size check
    ret, frame = cap.read()
    frame = resize_image(frame, scaling_ratio)
    frame = pickle.dumps(frame)
    size = len(frame)
    connection.sendall(bytes(str(size), 'utf-8'))
    print("Video server : Sent initial frame size.")

    frame_count = 0

    # todo break the following into functions for readability

    while True:
        if frame_count == 25:
            connection.sendall(pickle.dumps(datetime.now()))
            print("Video server : Sent own time to client.")
            frame_count = 0
            packet_latency = connection.recv(4096)
            print("Video server : Received back the packet latency.")
            packet_latency = pickle.loads(packet_latency)
            new_frame_size = int(MAX_LATENCY * 4096 / packet_latency)
            # todo use this to resize the frame, inform receiver, and deal with buffer problems
            # todo to resize the frame, we can have preset ratios and choose the closest one

            # For now we will find the new ratio
            # find the relative ratio compared to the current frame size
            relative_ratio = math.sqrt(new_frame_size / size)
            ret, frame = cap.read()
            if not ret:
                print("ERROR : couldn't read from webcam while resizing frame! (Unknown reason)")
                break
            frame = resize_image(frame, max(0.1, scaling_ratio * relative_ratio))
            new_size = len(pickle.dumps(frame))
            print("Video server : The new frame size is " + str(new_size))

            connection.sendall(bytes(str(new_size), 'utf-8'))

            ack = connection.recv(4096).decode('utf-8')

            if ack != "OK":
                print("Video server : Wrong final ack when resizing frame. (" + ack + ")")
            # Update things locally : Frame size and the scaling ratio
            size = new_size
            scaling_ratio *= relative_ratio
            scaling_ratio = max(scaling_ratio, 0.1)
            continue
        ret, frame = cap.read()

        frame = resize_image(frame, scaling_ratio)
        if not ret:
            print("Video server : ERROR : couldn't read from webcam ! (Unknown reason)")
            break
        frame = pickle.dumps(frame)
        frame_count += 1
        before_transmission = datetime.now()
        connection.sendall(frame)
        transmission_delay = datetime.now() - before_transmission
        transmission_delay = transmission_delay.total_seconds()
        if frame_count == 24:
            print("Video server : The transmission delay is : " + str(transmission_delay))
        time.sleep(0.02)  # todo not sure if this helps, or if the transmission delay is even relevant

    connection.close()
    cap.release()


class SendFrameThread(threading.Thread):
    def __init__(self, thread_id, name, counter):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.name = name
        self.counter = counter

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
        port = 12345
        s.bind(('', port))

        parallel_connections = 5
        s.listen(10)
        print('Video server : Socket created and listening.')

        cap = cv2.VideoCapture(0)
        print('Video server : Established webcam stream from main server thread.')

        streaming_threads = []
        for i in range(parallel_connections):
            connection, address = s.accept()
            print('Video server : Connection from ' + str(address) + f' (connection number {i})')

            # todo global cap object?
            new_thread = threading.Thread(target=video_stream, args=(connection,))
            new_thread.start()
            streaming_threads.append(new_thread)

        for th in streaming_threads:
            th.join()

        cap.release()
        s.close()
        print('Exiting video server.')
