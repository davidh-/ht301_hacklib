#!/usr/bin/python3 -u
import sys
import os
import cv2
import numpy as np

# Turn off debug output in ht301_hacklib to prevent print conflicts
import ht301_hacklib
ht301_hacklib.debug = 0

# Save original stdout, then make it binary unbuffered
original_stdout_fd = sys.stdout.fileno()
sys.stdout = os.fdopen(original_stdout_fd, 'wb', buffering=0)

# Initialize the thermal camera (with debug=0, no prints)
cap = ht301_hacklib.HT301(video_dev=0)

# Colormap (using JET like opencv_new defaults to index 9)
COLORMAP = cv2.COLORMAP_JET

frame_count = 0
error_count = 0
last_error_report = 0

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            error_count += 1
            # Only log every 100 errors to prevent log explosion
            if error_count - last_error_report >= 100:
                sys.stderr.write(f"Failed to read frame (total errors: {error_count})\n")
                sys.stderr.flush()
                last_error_report = error_count
            continue

        info, lut = cap.info()
        frame = frame.astype(np.float32)

        # Sketchy auto-exposure (same as opencv_new.py)
        frame -= frame.min()
        frame /= frame.max() + 1e-8  # Add epsilon to prevent division by zero
        frame = (frame * 255).astype(np.uint8)
        frame = cv2.applyColorMap(frame, COLORMAP)

        # Safety check - verify frame size
        expected_size = 384 * 288 * 3
        if frame.size != expected_size:
            sys.stderr.write(f"Wrong frame size: {frame.size}, expected {expected_size}\n")
            sys.stderr.flush()
            continue

        # Write frame to stdout (already binary, no .buffer needed)
        sys.stdout.write(frame.tobytes())

        frame_count += 1

        # Debug info every 100 frames
        if frame_count % 100 == 0:
            sys.stderr.write(f"Frames: {frame_count}\n")
            sys.stderr.flush()

except KeyboardInterrupt:
    sys.stderr.write("\nShutting down...\n")
    sys.stderr.flush()
except BrokenPipeError:
    sys.stderr.write("\nPipe broken, ffmpeg disconnected\n")
    sys.stderr.flush()
finally:
    cap.release()
