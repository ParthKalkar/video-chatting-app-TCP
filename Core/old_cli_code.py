from os import environ
from call_listener import *
from call_maker import *
from multiprocessing import Process, Pipe
import subprocess

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

# the following requires sudo access
# print("Freeing ports.")
# subprocess.call(['bash', './clear_ports.sh'])

print("Exiting main thread")
