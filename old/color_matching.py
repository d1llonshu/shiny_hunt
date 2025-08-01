from pygrabber.dshow_graph import FilterGraph
import cv2

def find_capture_device_id(max_tests=10):
    for device_id in range(max_tests):
        capture = cv2.VideoCapture(device_id)
        if capture is None or not capture.isOpened():
            if capture is not None:
                capture.release()
            continue

        ret, frame = capture.read()
        capture.release()

        if ret:
            print(f"Device ID {device_id} is available and returns valid frames.")
        else:
            print(f"Device ID {device_id} is available but does not return valid frames.")

# find_capture_device_id(10)

import numpy as np
from sklearn.cluster import KMeans

# === CONFIGURATION ===
x = 320  # x start (0,0 is top left)
y = 120    # y start
w = 320  # how much right
h = 360  # how much down
DEVICE_INDEX = 0  # Set this to your confirmed working device
CROP_REGION = (320, 0, 320, 240)  # (x, y, width, height) — tune for your Pokémon location
NUM_CLUSTERS = 2  # You can increase for more detail

# === Function: Get Dominant Colors with KMeans ===
def get_dominant_colors(image, k=2):
    # Reshape the image into a list of HSV pixels
    pixels = image.reshape((-1, 3)).astype(np.float32)

    # Run KMeans clustering
    kmeans = KMeans(n_clusters=k, n_init=10, random_state=0)
    kmeans.fit(pixels)

    return kmeans.cluster_centers_

# === Step 1: Open the capture device ===
cap = cv2.VideoCapture(DEVICE_INDEX, cv2.CAP_DSHOW)

# Set resolution (needed to avoid duplicating screen)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

ret, frame = cap.read()

if not ret:
    print("❌ Failed to capture frame. Make sure HDMI is active and OBS is closed.")
    exit()

# === Step 2: Crop the region of interest ===
# x, y, w, h = CROP_REGION
# roi = frame[y:y+h, x:x+w]
# roi=frame

if not cap.isOpened():
    print("❌ Failed to open capture device.")
    exit()

print("🎥 Streaming cropped top-right quadrant (Press ESC to quit)")

while True:
    ret, frame = cap.read()
    if not ret:
        print("⚠️ Failed to grab frame.")
        break

    # Crop top-right quadrant: (x=320, y=0, w=320, h=240)
    cropped = frame[0:240, 320:640]

    # Show the cropped feed
    cv2.imshow("Top-Right Crop", cropped)

    # Exit on ESC key
    if cv2.waitKey(1) == 27:
        print("🛑 Stream ended.")
        break

cap.release()
cv2.destroyAllWindows()

# Optional: Show the cropped region for tuning
# cv2.imshow("Cropped ROI", roi)
# cv2.waitKey(1000)  # <- waits until a key is pressed
# cv2.destroyAllWindows()
# cv2.imwrite("file.png", roi)
# # === Step 3: Convert to HSV ===
# hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

# # === Step 4: Get dominant HSV colors ===
# dominant_colors = get_dominant_colors(hsv_roi, k=NUM_CLUSTERS)

# print("🎨 Dominant HSV Colors (hue, saturation, value):")
# for idx, color in enumerate(dominant_colors):
#     h, s, v = color
#     print(f"  [{idx}] Hue: {h:.1f}, Saturation: {s:.1f}, Value: {v:.1f}")
