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
        print("Video server : Server IP : " + IP)
        s.bind((IP, port))
        s.listen(10)

        print('Video server : Socket created and listening.')

        connection, address = s.accept()

        print('Video server : Connection from ' + str(address))

        cap = cv2.VideoCapture(0)

        print('Video server : Established webcam stream.')

        scaling_ratio = 0.1

        ret, frame = cap.read()

        frame = resize_image(frame, scaling_ratio)

        frame = pickle.dumps(frame)

        size = len(frame)

        connection.sendall(bytes(str(size), 'utf-8'))
        print("Video server : Sent initial frame size.")

        frame_count = 0

        while True:
            if frame_count == 25:
                connection.sendall(pickle.dumps(datetime.now()))
                print("Video server : Sent own time to client.")
                frame_count = 0
                packet_latency = connection.recv(4096)
                print("Video server : Received back the packet latency.")
                packet_latency = pickle.loads(packet_latency)
                new_frame_size = int(MAX_LATENCY*4096/packet_latency)
                # todo use this to resize the frame, inform receiver, and deal with buffer problems
                # todo to resize the frame, we can have preset ratios and choose the closest one

                # For now we will find the new ratio
                # find the relative ratio compared to the current frame size
                relative_ratio = math.sqrt(new_frame_size/size)
                ret, frame = cap.read()
                if not ret:
                    print("ERROR : couldn't read from webcam while resizing frame! (Unknown reason)")
                    break
                frame = resize_image(frame, scaling_ratio*relative_ratio)
                new_size = len(pickle.dumps(frame))
                print("Video server : The new frame size is " + str(new_size))

                connection.sendall(bytes(str(new_size), 'utf-8'))

                ack = connection.recv(4096).decode('utf-8')

                if ack != "OK":
                    print("Video server : Wrong final ack when resizing frame. (" + ack + ")")
                # Update things locally : Frame size and the scaling ratio
            #     size = new_size
            #     scaling_ratio *= relative_ratio
            #     continue
            ret, frame = cap.read()

            # SHOW OWN WEBCAM
            # cv2.namedWindow('Your ugly face', cv2.WND_PROP_FULLSCREEN)
            # cv2.imshow('Your ugly face', frame)
            # cv2.waitKey(1)
            # todo check if the above works

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

        s.close()
        print('Exiting video server.')
