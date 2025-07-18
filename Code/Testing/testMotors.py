from gpiozero import Motor
from time import sleep
from gpiozero import DistanceSensor

# Using BCM numbering (GPIO numbers) matching your pinout
# Motor(forward, backward, enable, pwm=True)
leftMotor = Motor(forward=17, backward=27, enable=12, pwm=True)
rightMotor = Motor(forward=22, backward=23, enable=13, pwm=True)

  

try:
    print("Motor control test with correct pinout")
    
    # Test sequence
    print("Forward 50%")
    leftMotor.forward(0.5)
    rightMotor.forward(0.5)
    sleep(2)
    
    print("Forward 100%")
    leftMotor.forward(1.0)
    rightMotor.forward(1.0)
    sleep(2)
    
    print("Backward 30%")
    leftMotor.backward(0.3)
    rightMotor.backward(0.3)
    sleep(2)
    
    print("Stop")
    leftMotor.stop()
    rightMotor.stop()
    

except KeyboardInterrupt:
    print("\nStopped by user")

