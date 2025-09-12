import cv2
import numpy as np
import os
import json
import hashlib

from setup import CONFIG_PATH, HUNT_NAME_MANUAL

def parse_screenshots(path, attempts, bounding_box, ext="png"):
    x, y, w, h = bounding_box
    seen = set()
    reset_numbers = []

    for att in range(400):
        p = os.path.join(path, f"reset_{att}.{ext}")
        img = cv2.imread(p, cv2.IMREAD_COLOR)
        if img is None:
            print(f"Missing/unreadable: {p}")
            continue


        H, W = img.shape[:2]
        if not (0 <= x and 0 <= y and x+w <= W and y+h <= H):
            print(f"ROI out of bounds for {p}")
            continue
        
        roi = img[y:y+h, x:x+w]
        cv2.imshow("test", roi)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
       
        key = (roi.shape, roi.dtype.str, hashlib.md5(roi.tobytes()).hexdigest())

        if key not in seen:
            seen.add(key)
            reset_numbers.append(att)

        if att % 100 == 0:
            print(p)

    print(reset_numbers)
    return reset_numbers

if __name__ == "__main__":
    print("Before typing in the hunt name, please make sure the switch set up to recieve the first scripted input.")
    # hunt = input("hunt_name (case sensitive): ")
    hunt = HUNT_NAME_MANUAL
    try:
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
            data = config[hunt]
            screenshot_folder = data["path"] + "/screenshots/"
            attempts = data["resets"]
            bounding_box = data["shiny_bounding_box"]
            os.makedirs(screenshot_folder, exist_ok=True)
            f.close()
        
        print("Config verified")
        parse_screenshots(screenshot_folder, attempts, bounding_box)
    except Exception as e:
        print(f"Error with config or config path: {e}")
    