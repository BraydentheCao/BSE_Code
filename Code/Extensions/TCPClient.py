from flask import Flask, Response, render_template_string
import cv2
import numpy as numpy
from time import sleep
import time
import socket
import cv2
import mediapipe as mp
import math

# Computer

HOST = "192.168.68.82"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

app = Flask(__name__)


def fingerLength(base,tip):
    x_diff = base.x - tip.x
    y_diff = base.y - tip.y
    
    return math.sqrt(x_diff ** 2 + y_diff ** 2)

def fingerAngle(base,tip):
    # Handles for the undefined values of cot
    if base.x == tip.x: # 90
        if tip.y > base.y:
            return 90
        else: # 270
            return -90

    x = tip.x - base.x
    y = tip.y - base.y 
    
    return math.degrees(math.atan2(x,y))


# Open your computer's webcam (0 = default webcam)
camera = cv2.VideoCapture(0)

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            print("Camera not available")
            sleep(1)  # avoid tight infinite loop
            continue
            # Optional: resize or process frame here

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # insert code for index finder direction here
                # Hint: use the x and y coordinates of the joints :D
                mp.solutions.drawing_utils.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            # Add code here
            five = results.multi_hand_landmarks[5]
            eight = results.multi_hand_landmarks[8]
            
            angle = fingerLength(result)
            length = fingerLength(five,eight)

            print(f"Angle: {angle}")
            print(f"Length: {length}")

        cv2.imshow('Finger Direction Recognition', frame)


        

        """
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

        """

"""
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

if __name__ == '__main__':
    app.run(debug=True)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b"Hello, world")
    data = s.recv(1024)

print(f"Received {data!r}")

"""
