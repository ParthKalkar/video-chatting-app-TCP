from os import environ
from call_listener import *
from call_maker import *
from multiprocessing import Process, Pipe
import subprocess
from local_backend import *

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

print("Hello from Python!")
# GUI part
backend_server_redis()

print("Goodbye from Python.")
