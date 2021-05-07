from os import environ
from call_listener import *
from call_maker import *
from multiprocessing import Process, Pipe

# Logging
# todo elaborate the logging and actually use it
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Call listening port is 12344
# Video streaming port is 12345
# Audio streaming port is 12346

# CURRENT TODOLIST
# todo make the global variables part of classes
# todo solve all warnings
# todo plan the structure of files
# todo review the compatibility and performance of the libraries used (opencv and pyaudio)
# todo fix the thread names and numbers

environ["QT_DEVICE_PIXEL_RATIO"] = "0"
environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
environ["QT_SCREEN_SCALE_FACTORS"] = "1"
environ["QT_SCALE_FACTOR"] = "1"

# This part is a testing ground for processes and pipes


def process_test(pipe: Pipe):
    msg = pipe.recv()
    print(msg)
    print("Exiting child process.")


p1, p2 = Pipe()
child_process = Process(target=process_test, args=(p2,))
# child_process.start()
p1.send("Hello from parent (sent over the pipe).")

print("Welcome to the best video chat app in the world!")

# add the username to db and make him online
username = input("First of all, I would like to know your name : ")
signup(username)
go_online(username, get_my_private_ip())

print("Your private IP address : " + str(get_my_private_ip()))

choice = -1
while 1:
    # global choice
    choice = input("Do you wanna make a call? (y/n) : ")
    if choice == 'y' or choice == 'n':
        break
    else:
        print("Invalid input /!\\ please try again.")

try:
    if choice == 'n':
        t_init = CallListeningThread(30, "Listen for call", 30)
        t_init.start()
        t_init.join()
    else:
        t_listen = InitiateCallThread(30, "Make a call", 30)
        t_listen.start()
        t_listen.join()
except KeyboardInterrupt:
    # So that the user sign-off routine would work if I interrupt the program.
    print("Program stopped with a keyboard interrupt.")


# This will delete the user after he finishes
print("Signing off user")
go_offline(username)

print("Exiting main thread")
