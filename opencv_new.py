#!/usr/bin/python3
import numpy as np
import cv2
import ht301_hacklib
import utils
import time
import os
from tkinter import Tk, Label
from PIL import Image, ImageTk

# Initialize the thermal camera
cap = ht301_hacklib.HT301()

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', fourcc, 25.0, (640, 480))

# Set up the Tkinter window
root = Tk()
root.title("UAP Red Shift Detector - IR (Infrared) Thermal Camera")

# Set initial size of the window based on the video's resolution
initial_width = 640
initial_height = 480
root.geometry(f'{initial_width}x{initial_height}')  # Set the initial window size

label = Label(root)
label.pack(fill="both", expand=True)  # Make the video label expandable

def celsius_to_fahrenheit(celsius):
    return (celsius * 9/5) + 32


# Define the colormap cycle
colormap_cycle = [
    cv2.COLORMAP_AUTUMN, cv2.COLORMAP_BONE, cv2.COLORMAP_JET,
    cv2.COLORMAP_WINTER, cv2.COLORMAP_RAINBOW, cv2.COLORMAP_OCEAN,
    cv2.COLORMAP_SUMMER, cv2.COLORMAP_SPRING, cv2.COLORMAP_COOL,
    cv2.COLORMAP_HSV, cv2.COLORMAP_PINK, cv2.COLORMAP_HOT,
    cv2.COLORMAP_PARULA, cv2.COLORMAP_MAGMA, cv2.COLORMAP_INFERNO,
    cv2.COLORMAP_PLASMA, cv2.COLORMAP_VIRIDIS, cv2.COLORMAP_CIVIDIS,
    cv2.COLORMAP_TWILIGHT, cv2.COLORMAP_TWILIGHT_SHIFTED, cv2.COLORMAP_TURBO
]
current_cmap_index = 9


# Function to handle key presses
def on_key(event):
    global frame, current_cmap_index, colormap_cycle
    key = event.char
    if key == 'q':
        cap.release()
        out.release()
        root.destroy()  # Close the Tkinter window
    elif key == 'u':
        cap.calibrate()
    elif key == 's':
        cv2.imwrite(time.strftime("%Y-%m-%d_%H:%M:%S") + '.png', frame)
    elif key == ',':  # Go to the previous colormap
        current_cmap_index = (current_cmap_index - 1) % len(colormap_cycle)
    elif key == '.':  # Go to the next colormap
        current_cmap_index = (current_cmap_index + 1) % len(colormap_cycle)


# Bind the key press event to the handler
root.bind('<KeyPress>', on_key)

# Function to update the display and handle the video feed
def video_stream():
    global frame, resized_frame
    ret, frame = cap.read()
    if ret:
        info, lut = cap.info()
        frame = frame.astype(np.float32)

        # Sketchy auto-exposure
        frame -= frame.min()
        frame /= frame.max()
        frame = (np.clip(frame, 0, 1) * 255).astype(np.uint8)
        frame = cv2.applyColorMap(frame, colormap_cycle[current_cmap_index])

        # Convert temperatures from Celsius to Fahrenheit
        Tmin_F = celsius_to_fahrenheit(info['Tmin_C'])
        Tmax_F = celsius_to_fahrenheit(info['Tmax_C'])
        Tcenter_F = celsius_to_fahrenheit(info['Tcenter_C'])

        # Draw temperatures in Fahrenheit on the frame
        utils.drawTemperature(frame, info['Tmin_point'], Tmin_F, (55, 0, 0))
        utils.drawTemperature(frame, info['Tmax_point'], Tmax_F, (0, 0, 85))
        utils.drawTemperature(frame, info['Tcenter_point'], Tcenter_F, (0, 255, 255))



        # Keep the original frame aspect ratio or not, depending on your needs
        aspect_ratio = frame.shape[1] / frame.shape[0]  # width / height
        new_width = int(label.winfo_height() * aspect_ratio)
        new_size = (new_width, label.winfo_height())

        # Convert the frame to a format suitable for Tkinter
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_pil = Image.fromarray(frame)
        resized_frame = frame_pil.resize(new_size, Image.ANTIALIAS)
        frame_tk = ImageTk.PhotoImage(image=resized_frame)

        # Display the image on the label
        label.imgtk = frame_tk
        label.configure(image=frame_tk)

        # Write the frame to the output video file
        out.write(cv2.cvtColor(np.array(resized_frame), cv2.COLOR_RGB2BGR))

    # Call this function again after a short delay to update the video feed
    root.after(10, video_stream)


# Function to resize the image when the window is resized
def resize_image(event):
    global frame, resized_frame
    if frame is not None and (event.width, event.height) != (initial_width, initial_height):
        # Keep the original frame aspect ratio or not, depending on your needs
        aspect_ratio = frame.shape[1] / frame.shape[0]  # width / height
        new_width = int(event.height * aspect_ratio)
        new_size = (new_width, event.height)

        # Resize the original frame
        frame_pil = Image.fromarray(frame)
        resized_frame = frame_pil.resize(new_size, Image.ANTIALIAS)
        frame_tk = ImageTk.PhotoImage(image=resized_frame)

        # Update the label with the resized image
        label.imgtk = frame_tk
        label.configure(image=frame_tk)

# Bind the function to the window's resize event
root.bind('<Configure>', resize_image)

# Start the video stream
video_stream()

# Start the Tkinter event loop
root.mainloop()
