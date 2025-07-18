import RPi.GPIO as GPIO
from gpiozero import Motor
import time


rightMotor = Motor(forward=17, backward=27, enable=12, pwm=True)
leftMotor = Motor(forward=22, backward=23, enable=13, pwm=True)

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

def ultrasonicDistance(trigger, echo):
    GPIO.output(trigger, False)
    time.sleep(0.5)
    
    GPIO.output(trigger, True)
    time.sleep(0.00001)
    GPIO.output(trigger, False)


    pulse_start = time.time()
    while GPIO.input(echo) == 0:
        pulse_start = time.time()
        
    pulse_end = time.time()
    while GPIO.input(echo) == 1:
        pulse_end = time.time()
    pulse_duration = pulse_end - pulse_start
    return round(pulse_duration * 17150,3)

try:
    while True:
        distanceL = 0 #ultrasonicDistance(TRIGL, ECHOL)
        distanceR = 0 #ultrasonicDistance(TRIGR, ECHOR)
        distanceM = ultrasonicDistance(TRIGM, ECHOM)

        print(f"Left Distance: {distanceL} cm, Right Distance: {distanceR} cm, Middle Distance: {distanceM} cm")
       
        
        #speedLeft = distanceM*0.005+0.5  # Adjust speed based on distance
        if distanceM > 10 and distanceM < 100:
            speedLeft = distanceM*0.005+0.5
            leftMotor.forward(speedLeft)
            rightMotor.forward(speedLeft)
            time.sleep(.1)
        elif distanceM <= 10 and distanceM > 8:
            speedLeft = 0
            leftMotor.forward(speedLeft)
            rightMotor.forward(speedLeft)
            time.sleep(.1)
        elif distanceM <= 8:
            speedLeft = .35
            leftMotor.backward(speedLeft)
            rightMotor.backward(speedLeft)
            time.sleep(.1)
        else:
            leftMotor.forward(0)
            rightMotor.forward(0)

        
except KeyboardInterrupt:
    GPIO.cleanup()