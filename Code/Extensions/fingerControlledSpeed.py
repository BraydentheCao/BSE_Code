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

# Initialize PiCam
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)}))
picam2.start()

GPIO.setmode(GPIO.BCM)
TRIGL = 6
ECHOL = 5
GPIO.setup(TRIGL, GPIO.OUT)
GPIO.setup(ECHOL, GPIO.IN)

TRIGR = 26
ECHOR = 16
GPIO.setup(TRIGR, GPIO.OUT)
GPIO.setup(ECHOR, GPIO.IN)

TRIGM = 4
ECHOM = 25
GPIO.setup(TRIGM, GPIO.OUT)
GPIO.setup(ECHOM, GPIO.IN)

FRAME_WIDTH = 640
CENTER_X = FRAME_WIDTH // 2

counter = 0

prevErrorA = 0
curErrorA = 0
iErrorA = 0

prevErrorD = 0
curErrorD = 0
iErrorD = 0

'''
Takes in an offset and target, returns the speed of the turn speed needed using PID control
'''
def ballAnglePID(current, target):
    global prevErrorA, curErrorA, iErrorA
    
    if abs(current - target) < 50:
       return 0

    curErrorA = 0.0015625*2*(target - current)

    kp = 0.5 # Proportional gain
    kd = 0.1  # Derivative gain
    ki = 0.0000000001  # Integral gain

    dError = curErrorA - prevErrorA
    iErrorA += curErrorA  # Integral error can be implemented if needed

    P = kp * curErrorA
    I = ki * iErrorA
    D = kd * dError
    #print(f"PID - P: {P}, I: {I}, D: {D}, curError: {curError}, prevError: {prevError}, iError: {iError}")

    
    prevErrorA = curErrorA
    speed = P + D
    if speed > -1 and speed < 1:
        if speed < 0.4 and speed > 0:
            
            return 0.4
        elif speed > -0.4 and speed < 0:
            
            return -0.4
        else:
            return speed
    else:
        print("out of bounds")
        return 0

        
def measureBallDistance(r, offsetP):
    f = 290.562
    R = 17.78 # Radius of the ball in cm
    D = R*f/r
    offsetR = offsetP*D/f
    return D # Pythagorean theorem to find distance from camera to ball


def runUltrasonicDistance(trigger, echo):
    GPIO.output(trigger, False)
    time.sleep(0.0001)
    
    GPIO.output(trigger, True)
    time.sleep(0.0001)
    GPIO.output(trigger, False)
    
    pulse_start = time.time()
    while GPIO.input(echo) == 0:
        pulse_start = time.time()
        
    pulse_end = time.time()
    while GPIO.input(echo) == 1:
        pulse_end = time.time()
    pulse_duration = pulse_end - pulse_start
    return round(pulse_duration * 17150,3)

distanceFromBallCamera = 0
distanceFromBallUltrasonic = 0
centerCountFrames = 0
floorForwardCountFrames = 0



def track_red_ball(frame):
    global distanceFromBallCamera, distanceFromBallUltrasonic, centerCountFrames, floorForwardCountFrames

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
        ((x, y), radius) = cv2.minEnclosingCircle(largest)
        
        if M["m00"] != 0 and radius > 50:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            offset = cX - CENTER_X
            cv2.drawContours(frame, [largest], -1, (0, 255, 0), 2)
            cv2.circle(frame, (cX, cY), 5, (255, 0, 0), -1)
            cv2.line(frame, (cX, 0), (cX, frame.shape[0]), (255, 0, 0), 1)
            cv2.line(frame, (0, cY), (frame.shape[1], cY), (255, 0, 0), 1)
            
            '''
            #print(f"Ball center: {cX,cY}")
            #print(f"Ball radius: {radius:.2f} pixels")
            #distanceFromBallUltrasonic = runUltrasonicDistance(TRIGM, ECHOM) + 17.78/2
            #print(f"Distance from ball (camera): {distanceFromBallCamera:.3f} cm")
            #print(f"Distanec from ball (ultrasonic): {distanceFromBallUltrasonic:.3f} cm")
            '''
           
            # Calculate offset and position

            if abs(offset) < 50:
                position = "Centered"
            elif offset < 0:
                position = "Left"
            else:
                position = "Right"

            
            
            
            # Display info

            
            
            

            # First make sure ball is centered, then correct for distance
            '''
            if position == "Centered": # If distance is <20, then use ultrasonic sensor 
                
                print("if")
                
            '''
                

            #else:
            '''
            turnSpeed = ballAnglePID(cX,CENTER_X)
            print("hi")
            
            if turnSpeed > 0:
                if abs(offset) < 100:
                    print(f"Turn speed: {turnSpeed}")
                    rightMotor.forward(turnSpeed)
                    leftMotor.stop()
                    
                else:
                    print(f"Turn speed: {turnSpeed}")
                    rightMotor.forward(turnSpeed)
                    leftMotor.backward(turnSpeed)

            elif turnSpeed < 0:
                if abs(offset) < 100:
                    print(f"Turn speed: {turnSpeed}")
                    leftMotor.forward(-turnSpeed)
                    leftMotor.stop()

                else:
                    print(f"Turn speed: {turnSpeed}")
                    leftMotor.forward(-turnSpeed)
                    rightMotor.backward(-turnSpeed)

            else:
                leftMotor.stop()
                rightMotor.stop()

            
            
            if measureBallDistance(radius,offset) > 35:
                rightMotor.forward(.7)
                leftMotor.forward(.7)
                                  
            else:
                if turnSpeed > 0:
                    centerCountFrames = 0
                    if abs(offset) < 100:
                        print(f"Turn speed: {turnSpeed}")
                        rightMotor.forward(turnSpeed)
                        leftMotor.stop()
                        
                    else:
                        print(f"Turn speed: {turnSpeed}")
                        rightMotor.forward(turnSpeed)
                        leftMotor.backward(turnSpeed)

                elif turnSpeed < 0:
                    centerCountFrames = 0
                    if abs(offset) < 100:
                        print(f"Turn speed: {turnSpeed}")
                        leftMotor.forward(-turnSpeed)
                        leftMotor.stop()

                    else:
                        print(f"Turn speed: {turnSpeed}")
                        leftMotor.forward(-turnSpeed)
                        rightMotor.backward(-turnSpeed)

                else:
                    leftMotor.stop()
                    rightMotor.stop()
                    centerCountFrames += 1
                    
                if centerCountFrames > 5:
                    distanceFromBallCamera = measureBallDistance(radius,offset) - 17.78/2
                    distanceFromBallUltrasonic = runUltrasonicDistance(TRIGM, ECHOM)
                    if distanceFromBallCamera < 20 and distanceFromBallCamera > 8:
                        print("1")
                        if distanceFromBallUltrasonic < 12:                        
                            leftMotor.stop()
                            rightMotor.stop()  
                            print("Success!")
                        
                        else: 
                            leftMotor.forward(0.4)
                            rightMotor.forward(0.4)
                            print("Distance speed: 0.4, too far")
                    
                    elif distanceFromBallCamera < 8:
                        leftMotor.backward(0.5)
                        rightMotor.backward(0.5)
                        print("Distance speed: -0.4, too close")


                    else:
                        leftMotor.forward(0.35)
                        rightMotor.forward(0.35)
                        print("Distance speed: 0.4")
            
              
            cv2.putText(frame, f"Offset: {offset} | Position: {position}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 2)
            cv2.putText(frame, f"Ball distance (camera): {distanceFromBallCamera:.2f} | Ball distance (US): {distanceFromBallUltrasonic:.2f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 2)
        else:
            rightMotor.forward(.5)
            leftMotor.backward(.4)
            print(f"Nothing detected: Turning at 0.5")    
        '''
        
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