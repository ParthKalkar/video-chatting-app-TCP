import threading
import socket
import math
import requests

# correspondent_ip = ""

def get_my_public_ip():
    # return '85.26.165.173'
    # return '10.91.49.174'  # University student
    # return '10.241.1.187'  # Connecting to ethernet in my room

    r = requests.get(r'http://jsonip.com')
    ip = r.json()['ip']
    print('Your IP is', ip)
    return ip


def get_my_private_ip():
    # print(system('ifconfig'))
    # todo Understand what the following code does
    # todo Does this require Internet access to work?
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    res = s.getsockname()[0]
    s.close()
    return res