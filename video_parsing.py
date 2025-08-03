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

    # === Flash detection ===
    current_brightness = np.percentile(gray_blur, BRIGHTNESS_PERCENTILE)
    if brightness_baseline is None:
        brightness_baseline = current_brightness
        flash_detected = False
    else:
        brightness_baseline = FLASH_DECAY * brightness_baseline + (1 - FLASH_DECAY) * current_brightness
        flash_detected = (current_brightness - brightness_baseline) > BRIGHTNESS_THRESHOLD

    # === Brightest-pixel mask ===
    thresh_val = np.percentile(gray_blur, BRIGHTNESS_PERCENTILE)
    _, bright_mask = cv2.threshold(gray_blur, thresh_val, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
    bright_mask = cv2.morphologyEx(bright_mask, cv2.MORPH_OPEN, kernel)
    masked_gray = cv2.bitwise_and(gray_blur, gray_blur, mask=bright_mask)

    # === Sparkle/blob detection on masked brightest pixels ===
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
        # save masked overlay for debugging
        masked_vis = cv2.cvtColor(masked_gray, cv2.COLOR_GRAY2BGR)
        for kp in keypoints:
            pt = (int(kp.pt[0]), int(kp.pt[1]))
            radius = int(kp.size / 2) if hasattr(kp, "size") else 5
            cv2.circle(masked_vis, pt, radius, (0,255,255), 2)
        cv2.putText(masked_vis, f"Resets: {resets}", (5,20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
        fname = os.path.join(screenshot_folder, "shiny.png")
        cv2.imwrite(fname, masked_vis)


    # === Visualization: only ROI content with circles and bounding box ===
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
    enable_box = False
    ser = init_serial(settings["controller_com_port"])
    start_serial_reader(ser)

    global brightness_baseline, sparkle_history, cooldown_frames, should_screenshot, shiny_detected, resets
    
    cap = cv2.VideoCapture(settings["video_device_index"])
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, RESOLUTION_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, RESOLUTION_HEIGHT)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open camera {CAMERA_INDEX}")

    cv2.namedWindow("Live Shiny Detection", cv2.WINDOW_NORMAL)

    #technically there is room for crashing here, but its just assumed itll be fine given we have setup
    # key = ""
    # while True:
    #     ret, frame = cap.read()
    #     cv2.imshow("Live Shiny Detection", frame)
    #     key = cv2.waitKey(1)
    #     if key == 'r':
    #         break
        

    last_seen = ""
    while True:
        should_screenshot = False #only want this to be true for 1 frame per reset
        ret, frame = cap.read()
        
        if not ret:
            continue  # drop and try next frame
        
        # keep track of state of read line (it will tell this program when to run shiny check)
        # microcontroller will track time and announce state via serial (i.e 'start shiny check' or 'end shiny check')
        # this program will respond based on shiny check outcome (i.e '1' if we do another encounter or just nothing if we found shiny or smth)
        #if it changes from
        # crashes if commands change too fast. seems to be fine otherwise.
        #
        # Mask only the bounding box
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
                if shiny_detected == False and shiny_detected_audio == False:
                    resets += 1
                    async_controller_sequence(ser, '1')
            last_seen = ser_log
        text = f"Resets: {resets}"
        org = (10, 30)  # position (x, y) of baseline of text
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        thickness = 2
        org2 = (10, 60)
        if enable_box:
            trigger, processed_frame = process_frame(frame, settings["shiny_bounding_box"])
            cv2.putText(processed_frame, text, org, font, font_scale, (0, 0, 255), thickness, cv2.LINE_AA)
            cv2.putText(processed_frame, last_seen, org2, font, font_scale, (0, 0, 255), thickness, cv2.LINE_AA)
            cv2.imshow("Live Shiny Detection", processed_frame)
        else:
            cv2.putText(frame, text, org, font, font_scale, (0, 0, 255), thickness, cv2.LINE_AA)
            cv2.putText(frame, last_seen, org2, font, font_scale, (0, 0, 255), thickness, cv2.LINE_AA)
            cv2.imshow("Live Shiny Detection", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            with open(CONFIG_PATH, "w") as f:
                all_settings[hunt]["resets"] = resets
                json.dump(all_settings, f, indent=2)
                f.close()
            break
        if key == ord("s"):
            async_controller_sequence(ser, '1')
        if key == ord("a"):
            async_controller_sequence(ser, 'A')
        if key == ord("b"):
            async_controller_sequence(ser, 'B')
        if key == ord("u"):
            async_controller_sequence(ser, 'U')
        if key == ord("c"):
            with open(CONFIG_PATH, "w") as f:
                all_settings[hunt]["resets"] = resets
                json.dump(all_settings, f, indent=2)
                f.close()
            break
        # if key == ord("t"):
        #     enable_box = not enable_box
        # if key == ord("b"):
        #     enable_box = not enable_box

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
        # test = data["shiny_bounding_box"]
        # x, y, w, h = test
        # print(f"x:{x}, y:{y}, w:{w}, h:{h}")
        print("Config verified, launching video.")
        run_live(data, hunt, config)
    except Exception as e:
        print(f"Error with config or config path: {e}")
    
