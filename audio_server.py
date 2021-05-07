from root import *
import pyaudio


# Audio format
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

# Locks
audio_stream_lock = threading.Lock()

# Network info
parallel_connections = 30


def audio_stream(connection, stream):
    while True:
        try:
            audio_stream_lock.acquire()
            data = stream.read(CHUNK)
            audio_stream_lock.release()
        except Exception as e:
            print("Audio server : Exception while sending data : " + str(e))
            break
        connection.sendall(data)


class SendAudioFrameThread(threading.Thread):
    def __init__(self, thread_id, name, counter):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.name = name
        self.counter = counter

    def run(self) -> None:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
        port = 12346
        s.bind(('', port))

        s.listen(parallel_connections)

        print('Audio server : Socket for audio created and listening.')

        p = pyaudio.PyAudio()
        print(f'Audio server : Device count : {p.get_device_count()}')
        print("Audio server : audio device opened.")

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
        print("Audio server : Audio stream opened.")

        stream.start_stream()
        print("Audio server : Audio stream started.")

        threads = []

        for i in range(parallel_connections):
            connection, address = s.accept()
            print('Audio server : Connection for audio from ' + str(address))
            new_thread = threading.Thread(target=audio_stream, args=(connection, stream,))
            new_thread.start()
            threads.append(new_thread)

        for th in threads:
            th.join()

        stream.stop_stream()
        stream.close()
        p.terminate()
        s.close()
        print("Exiting audio server.")
