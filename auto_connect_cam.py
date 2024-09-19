import numpy as np
import cv2
import time

def reconenct_camera(camera_id):
    cap = cv2.VideoCapture(camera_id)
    while not cap.isOpened():
        print("Dang ket noi lai cam....")
        time.sleep(1)
        cap = cv2.VideoCapture(camera_id)
    return cap

cap = reconenct_camera(1)

while True:
    if cap.isOpened():
        ret, img = cap.read()
        if ret:
            cv2.imshow("Cam", img)
        else:
            print("Cam disconnected..........")
            cap = reconenct_camera(1)
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break
    else:
        print("Cam disconnected....")
        cap = reconenct_camera(1)
        
cap.release()
cv2.destroyAllWindows()