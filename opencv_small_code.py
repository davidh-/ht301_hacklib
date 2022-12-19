import numpy as np
import cv2

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_CONVERT_RGB, 0)
# Use raw mode
cap.set(cv2.CAP_PROP_ZOOM, 0x8004)
# Calibrate
#cap.set(cv2.CAP_PROP_ZOOM, 0x8000)
while(True):
    ret, frame = cap.read()

    frame = frame.reshape(292,384,2) # 0: LSB. 1: MSB
    # Remove the four extra rows
    frame = frame[:288,...]
    # Convert to uint16
    dt = np.dtype(('<u2', [('x', np.uint8, 2)]))
    frame = frame.view(dtype=dt).astype(np.float32)
    # Sketchy auto-exposure
    frame -= frame.min()
    frame /= frame.max()
    gray = np.clip(frame, 0, 1) ** (1/2.2)

    cv2.imshow('frame',gray)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
