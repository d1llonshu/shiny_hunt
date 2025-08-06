import cv2
import numpy as np
from collections import deque
import os
import json

from setup import setup, CONFIG_PATH
from audio_parsing import listen
from controller import *

# --- Configuration ---
CAMERA_INDEX = 0  # change if you have multiple cameras
# x, y, w, h; adjust to your encounter area
OUTPUT_FOLDER = "hunt/shaymin_bdsp/screenshots/"
RESOLUTION_HEIGHT = 1080
RESOLUTION_WIDTH = 1920
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Detection parameters
BRIGHTNESS_PERCENTILE = 97
BLOB_MIN_AREA = 500
BLOB_MAX_AREA = 5000
SPARKLE_COUNT_THRESHOLD = 5
WINDOW_SIZE = 5
FLASH_DECAY = 0.9
BRIGHTNESS_THRESHOLD = 40
COOLDOWN_PERIOD = 15

# State
brightness_baseline = None
sparkle_history = deque(maxlen=WINDOW_SIZE)
cooldown_frames = 0
resets = 0
should_screenshot = False
shiny_detected = False
screenshot_folder = ""
shiny_folder = ""

#For testing how many frames a shiny is eligible to be detected
frame_count = 0

# Blob detector for big bright sparkles
def make_blob_detector():
    params = cv2.SimpleBlobDetector_Params() # type: ignore
    params.filterByArea = True
    params.minArea = BLOB_MIN_AREA
    params.maxArea = BLOB_MAX_AREA
    params.filterByCircularity = False
    params.filterByColor = True
    params.blobColor = 255
    params.filterByInertia = False
    params.filterByConvexity = False
    params.minThreshold = 200
    params.maxThreshold = 255
    params.thresholdStep = 5
    try:
        return cv2.SimpleBlobDetector_create(params) # type: ignore
    except AttributeError:
        return cv2.SimpleBlobDetector(params) # type: ignore

detector = make_blob_detector()

def process_frame(frame, roi_rect):
    global brightness_baseline, cooldown_frames, sparkle_history, resets, shiny_detected, should_screenshot

    global frame_count
    
    x, y, w, h = roi_rect
    h_frame, w_frame = frame.shape[:2]
    # clamp ROI to frame bounds
    #      1120,450,590,440
    x = max(0, min(x, w_frame - 1))
    y = max(0, min(y, h_frame - 1))
    w = max(1, min(w, w_frame - x))
    h = max(1, min(h, h_frame - y))

    roi = frame[y:y+h, x:x+w]

    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    gray_blur = cv2.GaussianBlur(gray, (3,3), 0)

    # Flash detection
    current_brightness = np.percentile(gray_blur, BRIGHTNESS_PERCENTILE)
    if brightness_baseline is None:
        brightness_baseline = current_brightness
        flash_detected = False
    else:
        brightness_baseline = FLASH_DECAY * brightness_baseline + (1 - FLASH_DECAY) * current_brightness
        flash_detected = (current_brightness - brightness_baseline) > BRIGHTNESS_THRESHOLD

    # Brightest Pixel Mask
    thresh_val = np.percentile(gray_blur, BRIGHTNESS_PERCENTILE)
    _, bright_mask = cv2.threshold(gray_blur, thresh_val, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
    bright_mask = cv2.morphologyEx(bright_mask, cv2.MORPH_OPEN, kernel)
    masked_gray = cv2.bitwise_and(gray_blur, gray_blur, mask=bright_mask)

    # Sparkle/blob detection on masked brightest pixels
    try:
        keypoints = detector.detect(masked_gray)
    except Exception:
        keypoints = []

    sparkle_count = len(keypoints)
    sparkle_history.append(sparkle_count)
    avg_sparkles = sum(sparkle_history) / max(1, len(sparkle_history))
    sparkle_cluster = avg_sparkles >= SPARKLE_COUNT_THRESHOLD

    trigger = False
    if cooldown_frames > 0:
        cooldown_frames -= 1
    else:
        if flash_detected and sparkle_cluster:
            trigger = True
        elif sparkle_cluster:
            trigger = True

    if trigger:
        cooldown_frames = COOLDOWN_PERIOD
        shiny_detected = True
        fname = os.path.join(shiny_folder, f"shiny{frame_count}.png")
        frame_count += 1
        cv2.imwrite(fname, frame)
        # save masked overlay for debugging
        masked_vis = cv2.cvtColor(masked_gray, cv2.COLOR_GRAY2BGR)
        for kp in keypoints:
            pt = (int(kp.pt[0]), int(kp.pt[1]))
            radius = int(kp.size / 2) if hasattr(kp, "size") else 5
            cv2.circle(masked_vis, pt, radius, (0,255,255), 2)
        cv2.putText(masked_vis, f"Resets: {resets}", (5,20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
        fname = os.path.join(shiny_folder, "shiny_masked.png")
        cv2.imwrite(fname, masked_vis)

    # Visualization only ROI content with circles and bounding box
    #      1120,450,590,440
    display = frame.copy()
    # draw bounding box
    cv2.rectangle(display, (x,y), (x+w, y+h), (255, 0, 0), 2)
    # draw sparkles inside ROI
    for kp in keypoints:
        pt = (int(kp.pt[0]) + x, int(kp.pt[1]) + y)  # offset to full frame
        radius = int(kp.size / 2) if hasattr(kp, "size") else 5
        cv2.circle(display, pt, radius, (0,255,255), 2)
    if flash_detected:
        cv2.putText(display, "FLASH", (x+5, y+20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)
    if sparkle_cluster:
        cv2.putText(display, "SPARKLES", (x+5, y+45), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
    cv2.putText(frame, f"Resets: {resets}", (5,20),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
    if should_screenshot:
        fname = os.path.join(screenshot_folder, f"reset_{resets}.png")
        cv2.imwrite(fname, frame)
    return trigger, display

def run_live(settings, hunt_name, all_settings):
    #Start serial communication
    ser = init_serial(settings["controller_com_port"])
    start_serial_reader(ser)

    global brightness_baseline, sparkle_history, cooldown_frames, should_screenshot, shiny_detected, resets
    
    global frame_count

    #openCV display related values
    text_font = cv2.FONT_HERSHEY_SIMPLEX
    text_font_scale = 0.7
    text_thickness = 2
    row_one = (10, 30)
    row_two = (10, 60)
    green = (0, 0, 255)
    window_name = f"{hunt_name} Shiny Hunt"

    #Start Video Capture
    print(f"Starting Video Capture at Index [{settings['video_device_index']}]")
    # cap = cv2.VideoCapture("hunt/shaymin_bdsp/reference_images/sample_vid.mp4")
    cap = cv2.VideoCapture(settings["video_device_index"])
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, RESOLUTION_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, RESOLUTION_HEIGHT)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open camera {CAMERA_INDEX}")
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    last_seen = ""
    enable_box = False
    entering_holding_pattern = False

    while True:
        # TO SEE HOW MANY FRAMES IT WILL DETECT, MUST REMOVE BEFORE USE!!!
        # shiny_detected = False
        # frame_count += 1

        should_screenshot = False #only want this to be true for 1 frame per reset
        ret, frame = cap.read()
        
        if not ret:
            continue  # drop and try next frame
        
        # TO DO - FLUSH SERIAL ON RESTART? (add to init method)

        # If shiny has been detected audio or visual, we don't want any potential for input
        if not entering_holding_pattern:
            #Tracks most recent serial output from microcontroller, which dictates behavior.
            ser_log = get_latest_command()
            if ser_log is not None and ser_log != last_seen:
                if ser_log == "Start Shiny Check":
                    enable_box = True
                elif ser_log == "End Shiny Check":
                    enable_box = False
                elif ser_log == "Screenshot":
                    should_screenshot = True
                elif ser_log == "End Scripted Input":
                    audio_path = shiny_folder + "shiny.wav"
                    shiny_detected_audio = False
                    if os.path.isfile(audio_path):
                        shiny_detected_audio = True
                        entering_holding_pattern = True
                    if shiny_detected == False and shiny_detected_audio == False:
                        resets += 1
                        async_controller_sequence(ser, '1')
                last_seen = ser_log
            # TESTING
            if os.path.isfile(shiny_folder + "shiny.wav"):
                entering_holding_pattern = True
            

            #Display is different depending on if the shiny detection is enabled
            if enable_box:
                trigger, processed_frame = process_frame(frame, settings["shiny_bounding_box"])
                display_frame = processed_frame
                if trigger:
                    entering_holding_pattern = True
            else:
                display_frame = frame

            cv2.putText(display_frame, f"Resets: {resets}", row_one, 
                        text_font, text_font_scale, green, text_thickness, cv2.LINE_AA)
            cv2.putText(display_frame, last_seen, row_two, 
                        text_font, text_font_scale, (0, 0, 255), text_thickness, cv2.LINE_AA)
            cv2.imshow(window_name, display_frame)

            if shiny_detected == True:
                entering_holding_pattern = True

        #If shiny has been found, enter holding pattern
        else:
            cv2.putText(frame, f"RESETS: {resets}", row_one, 
                        text_font, text_font_scale, green, text_thickness, cv2.LINE_AA)
            cv2.putText(frame, "SHINY!!!!! Entering holding pattern.", row_two, 
                        text_font, text_font_scale, (0, 0, 255), text_thickness, cv2.LINE_AA)
            cv2.imshow(window_name, frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            with open(CONFIG_PATH, "w") as f:
                all_settings[hunt]["resets"] = resets
                json.dump(all_settings, f, indent=2)
                f.close()
            break

        #Inputs when window is selected, S to Start.
        if key == ord("s"):
            async_controller_sequence(ser, '1')
        if key == ord("a"):
            async_controller_sequence(ser, 'A')
        if key == ord("b"):
            async_controller_sequence(ser, 'B')
        if key == ord("u"):
            async_controller_sequence(ser, 'U')
        if key == ord("d"):
            async_controller_sequence(ser, 'D')
        if key == ord("t"):
            enable_box = not enable_box
        if key == ord("p"):
            entering_holding_pattern = True
        if key == ord("c") or key == ord("q"):
            with open(CONFIG_PATH, "w") as f:
                all_settings[hunt]["resets"] = resets
                json.dump(all_settings, f, indent=2)
                f.close()
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    #looks for HUNT_NAME in config.json
    print("Before typing in the hunt name, please make sure the switch set up to recieve the first scripted input.")
    # hunt = input("hunt_name (case sensitive): ")
    hunt = "shaymin_bdsp" #hard coding for testing right now
    try:
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
            data = config[hunt]
            shiny_folder = data["path"] + "/shiny_detected/"
            os.makedirs(shiny_folder, exist_ok=True)
            screenshot_folder = data["path"] + "/screenshots/"
            os.makedirs(screenshot_folder, exist_ok=True)
            resets = data["resets"]
            f.close()
        
        print("Config verified")
        run_live(data, hunt, config)
    except Exception as e:
        print(f"Error with config or config path: {e}")
    
