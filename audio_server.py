from root import *
import pyaudio


class SendAudioFrameThread(threading.Thread):
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

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
        port = 12346
        IP = ''
        print("Server IP : " + IP)
        s.bind((IP, port))
        s.listen(10)

        print('Socket for audio created and listening.')

        connection, address = s.accept()

        print('Connection for audio from ' + str(address))

        p = pyaudio.PyAudio()

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        stream.start_stream()

        while True:
            try:
                data = stream.read(CHUNK)
            except Exception as e:
                print(e)
                break
            connection.sendall(data)

        stream.stop_stream()
        stream.close()
        p.terminate()
        s.close()
        print("Exiting audio server.")
