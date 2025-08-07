import cv2
import json
import os
# import argparse

CONFIG_PATH = "roi_config.json"

def nothing(x):
    pass

def clamp(val, minimum, maximum):
    return max(minimum, min(maximum, val))

def create_window_and_trackbars(win_name, frame_shape):
    h, w = frame_shape[:2]
    cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
    cv2.createTrackbar("X", win_name, 0, w - 1, nothing)
    cv2.createTrackbar("Y", win_name, 0, h - 1, nothing)
    cv2.createTrackbar("W", win_name, w//4, w, nothing)
    cv2.createTrackbar("H", win_name, h//4, h, nothing)

def get_trackbar_roi(win_name, frame_shape):
    h, w = frame_shape[:2]
    x = cv2.getTrackbarPos("X", win_name)
    y = cv2.getTrackbarPos("Y", win_name)
    rw = cv2.getTrackbarPos("W", win_name)
    rh = cv2.getTrackbarPos("H", win_name)
    # clamp to frame
    x = clamp(x, 0, w-1)
    y = clamp(y, 0, h-1)
    rw = clamp(rw, 1, w - x)
    rh = clamp(rh, 1, h - y)
    return (x, y, rw, rh)

def load_saved_roi():
    if os.path.isfile(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                return tuple(json.load(f)["roi"])
        except Exception:
            pass
    return None

def save_roi(roi):
    with open(CONFIG_PATH, "w") as f:
        json.dump({"roi": list(roi)}, f)
    print(f"Saved ROI to {CONFIG_PATH}: {roi}")

def draw_roi_overlay(frame, roi, label=None):
    x, y, w, h = roi
    overlay = frame.copy()
    cv2.rectangle(overlay, (x, y), (x+w, y+h), (0, 255, 255), 2)
    if label:
        cv2.putText(overlay, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)
    return overlay

def process_image(path):
    img = cv2.imread(path)
    if img is None:
        raise RuntimeError(f"Failed to load image: {path}")
    win = "ROI Config"
    create_window_and_trackbars(win, img.shape)
    # load existing if any
    saved = load_saved_roi()
    if saved:
        x,y,rw,rh = saved
        cv2.setTrackbarPos("X", win, x)
        cv2.setTrackbarPos("Y", win, y)
        cv2.setTrackbarPos("W", win, rw)
        cv2.setTrackbarPos("H", win, rh)

    while True:
        roi = get_trackbar_roi(win, img.shape)
        display = draw_roi_overlay(img, roi, label=f"ROI {roi}")
        cv2.imshow(win, display)
        key = cv2.waitKey(30) & 0xFF
        if key == ord("q") or key == 27:
            break
        if key == ord("s"):
            save_roi(roi)
    cv2.destroyAllWindows()

def process_video(path):
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {path}")
    ret, frame = cap.read()
    if not ret:
        raise RuntimeError("Failed to read first frame from video")
    win = "ROI Config"
    create_window_and_trackbars(win, frame.shape)
    saved = load_saved_roi()
    if saved:
        x,y,rw,rh = saved
        cv2.setTrackbarPos("X", win, x)
        cv2.setTrackbarPos("Y", win, y)
        cv2.setTrackbarPos("W", win, rw)
        cv2.setTrackbarPos("H", win, rh)

    # allow scrubbing: show current frame, space to advance, a to go back
    frame_index = 0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    while True:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ret, frame = cap.read()
        if not ret:
            break
        roi = get_trackbar_roi(win, frame.shape)
        display = draw_roi_overlay(frame, roi, label=f"Frame {frame_index} ROI {roi}")
        cv2.imshow(win, display)
        key = cv2.waitKey(0) & 0xFF
        if key == ord("q") or key == 27:
            break
        elif key == ord("s"):
            save_roi(roi)
        elif key == ord(" "):  # forward one frame
            frame_index = min(frame_index + 1, total - 1)
        elif key == ord("a"):  # back one frame
            frame_index = max(frame_index - 1, 0)
        elif key == ord("f"):  # fast forward 10
            frame_index = min(frame_index + 10, total - 1)
        elif key == ord("b"):  # back 10
            frame_index = max(frame_index - 10, 0)
    cap.release()
    cv2.destroyAllWindows()

def main():
    IMAGE_PATH = "hunt/arceus_bdsp/reference_images/shiny.png"

    ext = os.path.splitext(IMAGE_PATH)[1].lower()
    if ext in [".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff"]:
        process_image(IMAGE_PATH)
    else:
        process_video(IMAGE_PATH)
    # print("Need to update PATH before using...")

if __name__ == "__main__":
    main()
