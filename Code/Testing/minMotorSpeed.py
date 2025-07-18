from gpiozero import Motor
from time import sleep
from gpiozero import DistanceSensor

# For carpet

# L298n
# leftMotor = Motor(forward=17, backward=27, enable=12, pwm=True)
# rightMotor = Motor(forward=22, backward=23, enable=13, pwm=True)

# L9110S
rightMotor = Motor(13,22)  # GPIO12 & GPIO16
leftMotor = Motor(12,23) # GPIO13 & GPIO19


# Min starting speed: 0.35
# Min turning speed: 0.37
try:
    while True:
        leftMotor.forward(0.34)
        rightMotor.forward(0.34)
except KeyboardInterrupt:
    leftMotor.stop()
    rightMotor.stop()
    print("\nMotors stopped safely.")
#For desk: 0.4