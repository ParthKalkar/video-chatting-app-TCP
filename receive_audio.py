from root import *
import pyaudio

audio_buffer = b""
audio_buffer_lock = threading.Lock()


class ReceiveAudioFrameThread(threading.Thread):
    def __init__(self, threadID, name, counter, correspondent_ip):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.correspondent_ip = correspondent_ip

    def run(self) -> None:
        CHUNK = 4096
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
        port = 12346
        IP = self.correspondent_ip
        s.connect((IP, port))

        print('Audio receiver : Connection established for audio.')
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
        print("Exiting audio receiving thread.")


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
            if len(audio_buffer) >= CHUNK * 10:
                audio_buffer_lock.acquire()
                stream.write(audio_buffer[:CHUNK * 5])
                audio_buffer = audio_buffer[CHUNK * 5:]
                audio_buffer_lock.release()
            else:
                print("Audio player : Buffer under-run (len of buffer < chunk * 10).")
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("Audio playing thread terminated.")
