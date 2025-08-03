from setup import setup
from audio_parsing import listen
from controller import *
from configuration import configureVideoDevice
import cv2


import threading

HUNT_NAME = "shaymin_bdsp"

# Single shared Event instance
# shiny_check = threading.Event()

def main():
    print("OpenCV version:", cv2.__version__)
    # cap = cv2.VideoCapture(2)
    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    # if not cap.isOpened():
    #     raise RuntimeError(f"Cannot open camera {2}")

    # cv2.namedWindow("Test", cv2.WINDOW_NORMAL)
    # while True:
    #     should_screenshot = False #only want this to be true for 1 frame per reset
    #     ret, frame = cap.read()
        
    #     if not ret:
    #         continue  # drop and try next frame

    #     cv2.imshow("Test", frame)

    #     key = cv2.waitKey(1) & 0xFF
    #     if key == ord("q"):
    #         break

    # cap.release()
    # cv2.destroyAllWindows()
if __name__ == "__main__":
    main()

    # two threads: one for audio one for video (maybe one for serial?) 
    # then just wait on the states of each thread
