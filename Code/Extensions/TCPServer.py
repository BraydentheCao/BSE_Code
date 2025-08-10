from flask import Flask, Response, render_template_string
import cv2, time, math, socket, json, queue
import numpy as np
from picamera2 import Picamera2
from gpiozero import Motor
import RPi.GPIO as GPIO

"""
This code runs on my Raspberry Pi and controls a two-motor robot using hand gesture data received via a
TCP socket connection. It listens for JSON messages containing the relative length and angle of the index
finger, computes motor speeds with a custom motorControl function that maps finger angle and length to 
various different motor speeds for turning and moving. It controls the motors via GPIO and PWM pins using
the gpiozero library. The program continuously accepts incoming connections, decodes JSON data, adjusts 
motor speeds accordingly, and sends back a "successful" message.

Here is how the algorithm moves the robot based on finger angle:
 0 to 8 deg - Drive forward
 8 to 50 deg - Forward pivot turn right
 50 to 95 deg - Foward tank turn right
 95 to 140 deg - Reverse pivot turn right
 140 to 172 deg - Reverse tank turn right
 172 to 180 deg - Drive backward

Exact same for 0 to -180, only the robot turns left

 _______                                                 __
/       \                                               /  |
$$$$$$$  |  ______    _______   ______          ______  $$/
$$ |__$$ | /      \  /       | /      \        /      \ /  |
$$    $$<  $$$$$$  |/$$$$$$$/ /$$$$$$  |      /$$$$$$  |$$ |
$$$$$$$  | /    $$ |$$      \ $$ |  $$ |      $$ |  $$ |$$ |
$$ |  $$ |/$$$$$$$ | $$$$$$  |$$ |__$$ |      $$ |__$$ |$$ |
$$ |  $$ |$$    $$ |/     $$/ $$    $$/       $$    $$/ $$ |
$$/   $$/  $$$$$$$/ $$$$$$$/  $$$$$$$/        $$$$$$$/  $$/
                              $$ |            $$ |          
                              $$ |            $$ |          
                              $$/             $$/          
"""

# Initialize the motors to specified GPIO and PWM pins
leftMotor = Motor(13,22) 
rightMotor = Motor(12,23)

def motorControl(length,angle):
 
    """
    Calculate motor speeds based on finger length and angle.
    - length: relative finger length (0 to 1)
    - angle: finger angle in degrees (-180 to 180)
    Returns (leftSpeed, rightSpeed) motor speeds.
    """
 
    #angleRad = math.radians(angle)
    S_MULT = 0.75 # Suppression multiplier
   
    if length == 0 and angle == 0: # If there are not hands in frame, motor will stop
        return 0,0

    if length > 1: # Prevent a length over 1
        length = 1
    if length < 0.35: # Add threshold speed
        length = 0.35
   
    length = length*0.3 + 0.35

    #angle = int(angle/5 + 2.5) * 5
   
    leftSpeed = 0
    rightSpeed = 0

    # LEFT TURN

    # Angle betw -8 and 8
    if angle >= -8 and angle < 8:
        leftSpeed = length
        rightSpeed = length

    # Angle betw 8 and 85
    if angle >= 8 and angle < 95:
        leftSpeed = length
       
        if angle >= 8 and angle <= 40: # When right turning, the right motor slows down
            rightSpeed = length * (-0.015625*angle+1)
       
        elif angle > 40 and angle < 50:
            rightSpeed = 0

        elif angle >= 50 and angle < 85:
            leftSpeed = leftSpeed*0.8
            rightSpeed = length * (-0.00857143*angle-0.0714286)

    # Angle betw 85 and 95


    if angle >= 85 and angle < 95:
        leftSpeed = length
        rightSpeed = -length
       
   
    # Angle betw 95 and 172
    if angle >= 95 and angle < 172:
        leftSpeed = -length
       
        if angle >= 95 and angle <= 130: # When right turning, the right motor slows down
            rightSpeed = length * (0.0142857*angle-2.35714)
       
        elif angle > 130 and angle < 140:
            rightSpeed = 0

        elif angle >= 140 and angle <= 172:
            leftSpeed = leftSpeed*.8
            rightSpeed = length * (0.009375*angle-0.8125)


    # Angle is > 172 or < -172
    if angle > 172 or angle < -172:
        rightSpeed = -length
        leftSpeed = -length


    # RIGHT TURN

    # Angle betw -8 and -95
    if angle <= -8 and angle > -95:
        print("right turn")
        rightSpeed = length
       
        if angle <= -8 and angle >= -40: # When right turning, the right motor slows down
            leftSpeed = length * (0.015625*angle+1.125)
       
        elif angle < -40 and angle > -50:
            leftSpeed = 0

        elif angle <= -50 and angle > -85:
            rightSpeed = rightSpeed*0.8
            leftSpeed = length * (-0.00571429*angle+0.314286)

    # Angle betw -85 and -95


    if angle <= -85 and angle > -95:
        rightSpeed = length
        leftSpeed = -length
       
   
    # Angle betw -95 and -172
    if angle <= -95 and angle > -172:
        rightSpeed = -length
       
        if angle <= -95 and angle >= -130: # When right turning, the right motor slows down
            leftSpeed = length * (-0.0142857*angle-2.35714)
       
        elif angle < -130 and angle > -140:
            leftSpeed = 0

        elif angle <= -140 and angle >= -172:
            rightSpeed = rightSpeed*.8
            leftSpeed = length * (-0.009375*angle-0.8125)
   


    return leftSpeed, rightSpeed


HOST = ''  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Waiting for connection on port {PORT}...")
    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        buffer = b""
        while True:
            data = conn.recv(1024)
            buffer += data
            if not data:
                print("hi")
                break
            # buffer += data # This was for echoing info back
            # Right now we want something

            try:
               
                # Try to decode a full JSON message
                decoded = buffer.decode("utf-8")
                message = json.loads(decoded)

                # Extract values
                relativeLength = message["relativeLength"]
                angleIndex = message["angleIndex"]
                frameCounter = message["frameCounter"]

               

                #time.sleep(0.5)
                leftSpeed, rightSpeed = motorControl(relativeLength,angleIndex)

                leftSpeed = round(leftSpeed, 3)
                rightSpeed = round(rightSpeed, 3)


                print(f"Angle: {angleIndex}")
                print(f"Left speed: {leftSpeed}")
                print(f"Right speed: {rightSpeed}")


                # Account for negative speed
                if leftSpeed > 0:
                    leftMotor.forward(leftSpeed)
                elif leftSpeed < 0:
                    leftMotor.backward(-leftSpeed)
                else:
                    leftMotor.stop()


                if rightSpeed > 0:
                    rightMotor.forward(rightSpeed)
                elif rightSpeed < 0:
                    rightMotor.backward(-rightSpeed)
                else:
                    rightMotor.stop()

                #print(f"Relative Length: {relativeLength:.3f}")
                #print(f"Angle Index: {angleIndex:.3f}")
                #print(f"Frame counter: {frameCounter:.3f}")

               
                #Send an acknowledgment (optional)
               

                conn.sendall(b"Successful")
               
               

                buffer = b""  # Clear buffer for next message
            except json.JSONDecodeError:
                # Partial message received, wait for more data
                continue
