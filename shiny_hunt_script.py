from setup import setup
from audio_parsing import listen
from controller import *
import time

import threading

HUNT_NAME = "shaymin_bdsp"

# Single shared Event instance
# shiny_check = threading.Event()

def main():
    settings = setup(HUNT_NAME)
    ser = init_serial(settings["controller_com_port"])
    # listen(settings["audio_device_index"])
    # shiny_check.set()
    # time.sleep(10)
    test_commands(ser)

if __name__ == "__main__":
    main()
