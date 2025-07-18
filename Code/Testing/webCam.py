from flask import Flask, Response, render_template_string
from picamera2 import Picamera2
import cv2
import numpy as np
from gpiozero import Motor
from time import sleep
import RPi.GPIO as GPIO
import time
import math

# L298n
# rightMotor = Motor(forward=17, backward=27, enable=12, pwm=True)
# leftMotor = Motor(forward=22, backward=23, enable=13, pwm=True)

# L9110S
leftMotor = Motor(12,23)  # GPIO12 & GPIO16
rightMotor = Motor(13,22) # GPIO13 & GPIO19

app = Flask(__name__)

# Open webcam (0 = default camera)
cap = cv2.VideoCapture(0)

# Define video codec and output file
fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Or 'MJPG', 'MP4V', etc.
out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (640, 480))

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Write frame to file
    out.write(frame)

    # Optional: show preview
    cv2.imshow('Recording', frame)

    # Press 'q' to stop recording
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
out.release()
cv2.destroyAllWindows()
print("Recording saved as output.avi")
