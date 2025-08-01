import cv2
import numpy as np
from collections import deque
import os

# --- Configuration ---
CAMERA_INDEX = 0  # change if you have multiple cameras
ROI = (1050, 360, 700, 630)  # x, y, w, h; adjust to your encounter area
OUTPUT_FOLDER = "hunt/shaymin_bdsp/calibration_images/"
RESOLUTION_HEIGHT = 1920
RESOLUTION_WIDTH = 1080
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
frame_idx = 0

# Blob detector for big bright sparkles
def make_blob_detector():
    params = cv2.SimpleBlobDetector_Params()
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
        return cv2.SimpleBlobDetector_create(params)
    except AttributeError:
        return cv2.SimpleBlobDetector(params)

detector = make_blob_detector()

def process_frame(frame, roi_rect):
    global brightness_baseline, cooldown_frames, sparkle_history, frame_idx

    x, y, w, h = roi_rect
    h_frame, w_frame = frame.shape[:2]
    # clamp ROI to frame bounds
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
        print(f"[Frame {frame_idx}] Shiny candidate! flash={flash_detected}, avg_sparkles={avg_sparkles:.2f}")
        # save masked overlay for debugging
        masked_vis = cv2.cvtColor(masked_gray, cv2.COLOR_GRAY2BGR)
        for kp in keypoints:
            pt = (int(kp.pt[0]), int(kp.pt[1]))
            radius = int(kp.size / 2) if hasattr(kp, "size") else 5
            cv2.circle(masked_vis, pt, radius, (0,255,255), 2)
        cv2.putText(masked_vis, f"Frame {frame_idx}", (5,20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
        fname = os.path.join(OUTPUT_FOLDER, f"masked_overlay_live_{frame_idx}.png")
        cv2.imwrite(fname, masked_vis)

    # === Visualization: only ROI content with circles and bounding box ===
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

    return trigger, display

def run_live():
    global frame_idx, brightness_baseline, sparkle_history, cooldown_frames
    enable_box = False
    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, RESOLUTION_HEIGHT)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, RESOLUTION_WIDTH)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open camera {CAMERA_INDEX}")

    cv2.namedWindow("Live Shiny Detection", cv2.WINDOW_NORMAL)

    while True:
        ret, frame = cap.read()
        if not ret:
            continue  # drop and try next frame
        
        if enable_box:
            trigger, output = process_frame(frame, ROI)
            cv2.imshow("Live Shiny Detection", output)
        else:
            cv2.imshow("Live Shiny Detection", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        if key == ord("s"):
            enable_box = not enable_box
        frame_idx += 1

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_live()
