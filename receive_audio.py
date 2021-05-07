from root import *
import pyaudio


# Audio info
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

# Buffers and locks
audio_buffer = b""
audio_buffer_lock = threading.Lock()

# Connection info
parallel_connections = 20


def new_connection(ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
    port = 12346
    s.connect((ip, port))
    return s


def receive_audio(s):
    audio_data = s.recv(CHUNK)
    while 1:  # audio_data != "": # todo check which condition is better for the while loop
        global audio_buffer
        try:
            audio_data = s.recv(CHUNK)
            audio_buffer_lock.acquire()
            audio_buffer += audio_data
            audio_buffer_lock.release()
        except socket.error:
            print("Audio receiver : Server disconnected.")
            break


class ReceiveAudioFrameThread(threading.Thread):
    def __init__(self, thread_id, name, counter, correspondent_ip):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.name = name
        self.counter = counter
        self.correspondent_ip = correspondent_ip

    def run(self) -> None:

        threads = []

        for i in range(parallel_connections):
            s = new_connection(self.correspondent_ip)
            new_thread = threading.Thread(target=receive_audio, args=(s,))
            new_thread.start()
            threads.append(new_thread)

        for th in threads:
            th.join()

        print('Audio receiver : Connection established for audio.')
        print("Exiting audio receiving thread.")


class PlayAudioThread(threading.Thread):
    def __init__(self, thread_id, name, counter):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.name = name
        self.counter = counter

    def run(self) -> None:
        p = pyaudio.PyAudio()  # todo fix the bug with this shit (only happens when not using localhost)
        print("Audio player : Audio device opened.")
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        output=True,
                        frames_per_buffer=CHUNK)
        print("Audio player : Audio stream opened.")
        stream.start_stream()
        print("Audio player : Audio stream started.")
        while True:
            global audio_buffer
            if len(audio_buffer) >= CHUNK * 5:
                audio_buffer_lock.acquire()
                stream.write(audio_buffer[:5*CHUNK])
                audio_buffer = audio_buffer[5*CHUNK:]
                audio_buffer_lock.release()
            # Just for debugging (to see if we are having under runs)
            # else:
            #     print("Audio player : Buffer under-run (len of buffer < chunk * 10).")
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("Audio playing thread terminated.")
