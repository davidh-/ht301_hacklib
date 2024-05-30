#!/usr/bin/python3
import numpy as np
import cv2
import math
import ht301_hacklib
import utils
import time
import os

os.environ["DISPLAY"] = ":0.0"
os.environ["XAUTHORITY"] = "/home/pi/.Xauthority"

draw_temp = True

cap = ht301_hacklib.HT301()
cv2.namedWindow("HT301", cv2.WINDOW_NORMAL)

# Set the window location and size
cv2.moveWindow("HT301", 645, 37)
cv2.resizeWindow("HT301", 640, 480)

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'X264')
out = cv2.VideoWriter('output.avi', fourcc, 25.0, (640,480))

while(True):
    ret, frame = cap.read()

    info, lut = cap.info()
    frame = frame.astype(np.float32)

    # Sketchy auto-exposure
    frame -= frame.min()
    frame /= frame.max()
    frame = (np.clip(frame, 0, 1)*255).astype(np.uint8)
    frame = cv2.applyColorMap(frame, cv2.COLORMAP_BONE)

    if draw_temp:
        utils.drawTemperature(frame, info['Tmin_point'], info['Tmin_C'], (55,0,0))
        utils.drawTemperature(frame, info['Tmax_point'], info['Tmax_C'], (0,0,85))
        utils.drawTemperature(frame, info['Tcenter_point'], info['Tcenter_C'], (0,255,255))

    # Write the frame to the output video file
    out.write(frame)

    cv2.imshow('HT301',frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    if key == ord('u'):
        cap.calibrate()
    if key == ord('s'):
        cv2.imwrite(time.strftime("%Y-%m-%d_%H:%M:%S") + '.png', frame)

cap.release()
out.release()
cv2.destroyAllWindows()
