from flask import Flask, Response, render_template_string
import cv2
import numpy as numpy
from time import sleep
import time
import math
import cv2
import mediapipe as map

import socket

HOST = "192.168.68.82"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

mp_hands = map.solutions.hands
hands = mp_hands.Hands()

app = Flask(__name__)

# Open your computer's webcam (0 = default webcam)
camera = cv2.VideoCapture(0)

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            print("Camera not available")
            sleep(1)  # avoid tight infinite loop
            break
            # Optional: resize or process frame here





        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return '''
    <html>
        <body>
            <h1>Webcam Feed</h1>
            <img src="/video">
        </body>
    </html>
    '''

@app.route('/video')
def video():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
'''
if __name__ == '__main__':
    app.run(debug=True)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b"Hello, world")
    data = s.recv(1024)

print(f"Received {data!r}")
'''

