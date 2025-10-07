# Thermal Camera Interference Issue

## Problem
OpenCV `cap.read()` fails with V4L2 select() timeout when trying to read from T3-Search thermal camera at `/dev/video0`.

## Root Cause
Multiple thermal cameras running simultaneously causes interference:
- T3-Search camera: `/dev/video0`, `/dev/video1`
- Camera (thermal): `/dev/video2`, `/dev/video3` - **ALREADY IN USE by ffmpeg**
- HD USB Camera: `/dev/video4`, `/dev/video5`

Current running processes:
```
ffmpeg -f v4l2 ... -i /dev/video2 ... rtsp://127.0.0.1:8554/thermal
```

The kernel workers `[kworker/u9:*-uvcvideo]` are heavily loaded processing both cameras.

## Solutions

### Option 1: Stream with ffmpeg Instead of OpenCV
Use ffmpeg to capture and stream T3-Search, then read from RTSP stream in Python:

```bash
# Stream T3-Search with ffmpeg
ffmpeg -f v4l2 -framerate 25 -video_size 384x292 -i /dev/video0 \
  -c:v libx264 -preset veryfast -tune zerolatency \
  -x264-params keyint=30:min-keyint=30:no-scenecut=1:bframes=0 \
  -pix_fmt yuv420p -profile:v baseline \
  -f rtsp rtsp://127.0.0.1:8554/t3search
```

Then in Python:
```python
import cv2
cap = cv2.VideoCapture('rtsp://127.0.0.1:8554/t3search')
```

**Pros:**
- Both cameras can run simultaneously
- Consistent with existing setup
- Can access from multiple processes

**Cons:**
- Adds encoding/decoding overhead
- Loses raw thermal data (gets encoded as YUYV/H264)
- May affect thermal calibration data in metadata

### Option 2: Stop Other Camera and Use OpenCV Directly
Kill the ffmpeg process using `/dev/video2`:

```bash
pkill -f "ffmpeg.*video2"
```

**Pros:**
- Direct access to raw thermal data
- Full control over camera settings
- Proper calibration via `cap.set(cv2.CAP_PROP_ZOOM, 0x8000)`

**Cons:**
- Can only use one thermal camera at a time
- Loses streaming capability for the other camera

### Option 3: USB Bandwidth Optimization
Reduce bandwidth usage to allow both cameras:

1. Lower framerate on one or both cameras
2. Use different USB controllers if available
3. Reduce resolution (if supported)
4. Check USB hub configuration

### Option 4: Hybrid Approach
Use ffmpeg for the secondary camera (`/dev/video2`) and OpenCV direct access for primary T3-Search:

```bash
# Keep video2 on ffmpeg
# Use opencv_new.py for video0
```

This works if video0 isn't being accessed by anything else.

## Recommended Approach

**For thermal imaging work requiring raw data:** Use Option 2 (stop other camera, use OpenCV directly)

**For dual-camera streaming:** Use Option 1 (stream both with ffmpeg)

## Testing
Check what's using each device:
```bash
fuser /dev/video0 /dev/video1 /dev/video2
lsof | grep /dev/video
```

Check USB bandwidth:
```bash
usb-devices | grep -A 10 "T3-Search"
```
