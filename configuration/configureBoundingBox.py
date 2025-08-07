import cv2
import numpy as np

def nothing(x):
    pass

RESOLUTION_HEIGHT = 1080
RESOLUTION_WIDTH = 1920

def validateBoundingBox(boundingBox):
    #X, Y, L, W
    try:
        if boundingBox[0]+boundingBox[2] > RESOLUTION_WIDTH or boundingBox[1]+boundingBox[3] > RESOLUTION_HEIGHT:
            print("Failed bounding box validation (Won't fit in resolution).")
            return False
        elif boundingBox[0] < 0 or boundingBox[1] < 0 or boundingBox[2] < 0 or boundingBox[3] < 0:
            print("Failed bounding box validation (negative value)")
            return False
        else:
            return True
    except:
        print("Bad bounding box args.")
        return False

def setup(deviceIndex: int, bounding_box=None):
    if bounding_box:
        print(f"Manually Provided Bounding Box: {bounding_box}")
        return bounding_box
    print("Setting up Bounding Box...")
    print("Window may to a few seconds to load")
    print("Press S or Close the Window to Save")
    cap = cv2.VideoCapture(deviceIndex, cv2.CAP_MSMF) #set to msmf to better handle capture cards
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, RESOLUTION_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, RESOLUTION_HEIGHT)
    if not cap.isOpened():
        raise RuntimeError("Could not open video stream")

    # read one frame to get dimensions
    ret, frame = cap.read()
    if not ret:
        cap.release()
        raise RuntimeError("Couldn't read frame for sizing")
    height, width = frame.shape[:2]

    # no-op callback for trackbars
    def nothing(*args): pass

    cv2.namedWindow("Stream")
    cv2.createTrackbar("X", "Stream", 0, width, nothing)
    cv2.createTrackbar("Y", "Stream", 0, height, nothing)
    cv2.createTrackbar("W", "Stream", width // 4, width, nothing)
    cv2.createTrackbar("H", "Stream", height // 4, height, nothing)

    roi = (0, 0, 0, 0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # read sliders
        x = cv2.getTrackbarPos("X", "Stream")
        y = cv2.getTrackbarPos("Y", "Stream")
        w = cv2.getTrackbarPos("W", "Stream")
        h = cv2.getTrackbarPos("H", "Stream")

        # clamp to keep box in bounds
        if x + w > width:
            w = width - x
            cv2.setTrackbarPos("W", "Stream", w)
        if y + h > height:
            h = height - y
            cv2.setTrackbarPos("H", "Stream", h)

        roi = (x, y, w, h)

        # draw box + label
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)
        cv2.putText(frame, f"ROI=({x},{y},{w},{h})",
                    (10, height-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 1)

        cv2.imshow("Stream", frame)

        key = cv2.waitKey(1) & 0xFF
        # press 's' to save & exit
        if key == ord('s'):
            break
        # if window was closed manually
        if cv2.getWindowProperty("Stream", cv2.WND_PROP_VISIBLE) < 1:
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"Bounding Box Selected: {roi}")
    return roi