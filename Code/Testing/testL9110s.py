from gpiozero import Motor
from time import sleep


# Initialize motors
rightMotor = Motor(12,23)  # GPIO12 & GPIO16
leftMotor = Motor(13,22)  # GPIO13 & GPIO19

try:
    print("Controlling dual motors with L9110S...")
    while True:
        # Forward at 50% speed
        rightMotor.forward(0.5)
        leftMotor.forward(0.5)
        print("Motor A: Forward (50%)")
        sleep(2)
        
        # Reverse at 50% speed
        rightMotor.backward(0.5)
        leftMotor.backward(0.5)
        print("Motor B: Reverse (75%)")
        sleep(2)
        
        # Stop both motors
        leftMotor.stop()
        rightMotor.stop()
        print("Motors Stopped")
        sleep(1)

except KeyboardInterrupt:
    leftMotor.stop()
    rightMotor.stop()
    print("\nMotors stopped safely.")