from flask import Flask, Response, render_template_string
from picamera2 import Picamera2
import cv2
import numpy as np
from gpiozero import Motor
from time import sleep

# L298n
# rightMotor = Motor(forward=17, backward=27, enable=12, pwm=True)
# leftMotor = Motor(forward=22, backward=23, enable=13, pwm=True)

# L9110S
leftMotor = Motor(12,23)  # GPIO12 & GPIO16
rightMotor = Motor(13,22) # GPIO13 & GPIO19

app = Flask(__name__)

# Initialize PiCam
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)}))
picam2.start()

FRAME_WIDTH = 640
CENTER_X = FRAME_WIDTH // 2

counter = 0

prevError = 0
curError = 0
iError = 0

totalFocalLength = 0
counter = 0

'''
Takes in an offset and target, returns the speed of the turn speed needed using PID control
'''
def track_red_ball(frame):
    global totalFocalLength, counter
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([179, 255, 255])
    
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)
    
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    countours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if countours:
        largest = max(countours, key=cv2.contourArea)
        M = cv2.moments(largest)
        ((x, y), r) = cv2.minEnclosingCircle(largest)
        
        if M["m00"] != 0 and r > 5:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            offset = cX - CENTER_X
            cv2.drawContours(frame, [largest], -1, (0, 255, 0), 2)
            cv2.circle(frame, (cX, cY), 5, (255, 0, 0), -1)
            cv2.line(frame, (cX, 0), (cX, frame.shape[0]), (255, 0, 0), 1)
            cv2.line(frame, (0, cY), (frame.shape[1], cY), (255, 0, 0), 1)
            print(f"Ball center: {cX,cY}")
            print(f"Ball radius: {r:.2f} pixels")
            
            R = 7
            D = 12 
            f = r*D/R
            print(f"focal length: {f}")

            counter += 1
            totalFocalLength += f
            if counter > 0:
                averageFocalLength = totalFocalLength / counter
                print(f"Average focal length: {averageFocalLength:.5f} pixels")
            
            if abs(offset) < 30:
                position = "Centered"
            elif offset < 0:
                position = "Left"
            else:
                position = "Right"


            cv2.putText(frame, f"Offset: {offset} | Position: {position}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
            cv2.putText(frame, f"Ball center: {cX,cY} | Ball radius: {r:.2f} pixel | Average Focal length: {averageFocalLength}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

    return frame

def generate_frames():
    while True:
        frame = picam2.capture_array()
        # frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        frame = track_red_ball(frame)
        ret, buffer = cv2.imencode('.jpg', frame)
        jpg_frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n'
               b'Content-Length: ' + f"{len(jpg_frame)}".encode() + b'\r\n\r\n' +
               jpg_frame + b'\r\n')
        
@app.route('/')
def index():
    return render_template_string('''
        <html>
            <head><title>Red Ball Tracking Stream</title></head>
            <body>
                <h2>Live Tracking</h2>
                <img src="/video_feed">
            </body>
        </html>
    ''')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)