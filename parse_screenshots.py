import cv2
import numpy
import os
import json

from setup import CONFIG_PATH

def parse_screenshots(path):
    unique = []


if __name__ == "__main__":
    print("Before typing in the hunt name, please make sure the switch set up to recieve the first scripted input.")
    # hunt = input("hunt_name (case sensitive): ")
    hunt = "shaymin_bdsp" #hard coding for testing right now
    try:
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
            data = config[hunt]
            screenshot_folder = data["path"] + "/screenshots/"
            os.makedirs(screenshot_folder, exist_ok=True)
            f.close()
        
        print("Config verified")
        parse_screenshots(screenshot_folder)
    except Exception as e:
        print(f"Error with config or config path: {e}")
    