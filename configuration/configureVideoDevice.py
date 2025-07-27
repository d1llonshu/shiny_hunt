import cv2
import numpy as np
import time
import os

from configuration.configHelper import clear_folder, print_linebreak, VIDEO_SAMPLES_PATH

CAPTURE_DURATION = 2
MAX_INDEX = 4

def list_video_devices():
    """
    Try to open device indices 0..max_index‑1 and return those that succeed.
    """
    
    available = []
    for i in range(MAX_INDEX):
        print(f"Testing video input index: [{i}]")
        try:
            if saveSampleVideo(i) == True:
                available.append(i)
        except:
            print(f"Device Index out of Range: [{i}]")
    
    return available

def saveSampleVideo(i) -> bool:
    cap = cv2.VideoCapture(i, cv2.CAP_ANY)
    if not cap.isOpened():
        print("Cannot open camera")
        return False
    else:
        # Define the codec and create VideoWriter object
        out_path = os.path.join(VIDEO_SAMPLES_PATH, f"{i}.avi")
        fourcc = cv2.VideoWriter.fourcc(*'XVID')
        out = cv2.VideoWriter(out_path, fourcc, 20.0, (640,  480))

        start_time = time.time()
        while( int(time.time() - start_time) < CAPTURE_DURATION):
            ret, frame = cap.read()
            if not ret:
                break
            else:
                frame = cv2.flip(frame,0)

                # write the flipped frame
                out.write(frame)

                cv2.imshow('frame',frame)

        # Release everything if job is finished
        cap.release()
        out.release()
        cv2.destroyAllWindows()
        return True
                

def isInt(givenInput):
    try:
        max_index = int(givenInput)
        return max_index
    except:
        return -1

def setup(index=None) -> int:
    if index != None:
        print(f"Manually Provided Video Device Index: [{index}] ")
        return index
    clear_folder(VIDEO_SAMPLES_PATH)
    print(f"Max video input index {MAX_INDEX}")
    devices = list_video_devices()
    if len(devices) == 0:
        raise ValueError("No video input devices were found. Please double check that a video source is plugged in OR manually increase the MAX_INPUT value in configureVideoDevice.py.")
    elif len(devices) == 1:
        print_linebreak()
        print("There was only 1 available device. It will be automatically selected.")
        print(f"Device Index: {devices[0]}")
        return devices[0]

    else:
        print("There is more than 1 available device.")
        print("You can look at samples/audio_setup_files/index.avi to watch to the recordings.")
        print("If none of the records show the correct input, you'll have to terminate this and manually increase the MAX_INPUT value in configureVideoDevice.py.") 
        print("Available device indices:", devices)
        while True:
            choice = input("Enter the device index you'd like to use: ")
            if choice.isdigit() and int(choice) in devices:
                print(f"Selected device index {int(choice)}.")
                return int(choice)
            print(f"Invalid choice '{choice}'. Please choose from {devices}.")
