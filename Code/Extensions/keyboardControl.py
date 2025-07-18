import sys
import termios
import tty
import time
import select
import RPi.GPIO as GPIO

from gpiozero import Motor  # Or your motor library

# Setup your motors
leftMotor = Motor(12,23)  # GPIO12 & GPIO16
rightMotor = Motor(13,22) # GPIO13 & GPIO19


def get_key_nonblocking(timeout=0.0001):
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        rlist, _, _ = select.select([fd], [], [], timeout)
        if rlist:
            return sys.stdin.read(1)
        return None
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

print("Use WASD to move, Q to quit.")

STOP_DELAY = 0.5  # seconds to wait before stopping motors
last_key_time = 0
held_key = None
motors_running = False

while True:
    key = get_key_nonblocking()

    if key:
        key = key.lower()
        last_key_time = time.time()
        held_key = key

        if key == 'q':
            leftMotor.stop()
            rightMotor.stop()
            print("Exiting...")
            break
    else:
        # If no key detected, but a key was recently held, keep it
        if held_key and (time.time() - last_key_time) > STOP_DELAY:
            held_key = None  # clear held key after timeout

    # Control motors based on held_key
    if held_key == 'w':
        leftMotor.forward(0.6)
        rightMotor.forward(0.6)
        motors_running = True
    elif held_key == 'a':
        leftMotor.stop()
        rightMotor.forward(0.6)
        motors_running = True
    elif held_key == 's':
        leftMotor.backward(0.6)
        rightMotor.backward(0.6)
        motors_running = True
    elif held_key == 'd':
        leftMotor.forward(0.6)
        rightMotor.stop()
        motors_running = True
    else:
        if motors_running:
            leftMotor.stop()
            rightMotor.stop()
            motors_running = False