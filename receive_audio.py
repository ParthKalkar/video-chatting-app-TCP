from root import *
import pyaudio


audio_buffer = b""
audio_buffer_lock = threading.Lock()

class ReceiveAudioFrameThread(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self) -> None:
        """ for x in range(0, p.get_device_count()):
            info = p.get_device_info_by_index(x)
            print(info)"""
        CHUNK = 4096
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
        port = 12346
        IP = correspondent_ip
        s.connect((IP, port))

        print('Connection established for audio.')
        audio_data = s.recv(CHUNK)
        while audio_data != "":
            global audio_buffer
            try:
                audio_data = s.recv(CHUNK)
                audio_buffer_lock.acquire()
                audio_buffer += audio_data
                audio_buffer_lock.release()
            except socket.error:
                print("Server disconnected.")
                break


class PlayAudioThread(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self) -> None:
        CHUNK = 4096
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        p = pyaudio.PyAudio()  # todo fix the bug with this shit (only happens when not using localhost)
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        output=True,
                        frames_per_buffer=CHUNK)
        stream.start_stream()
        print("Audio device started.")
        while True:
            global audio_buffer
            if len(audio_buffer) >= CHUNK * 10:
                audio_buffer_lock.acquire()
                stream.write(audio_buffer[:CHUNK * 5])
                audio_buffer = audio_buffer[CHUNK * 5:]
                audio_buffer_lock.release()
        stream.stop_stream()
        stream.close()
        p.terminate()