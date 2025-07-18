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
        distanceL = ultrasonicDistance(TRIGL, ECHOL)
        distanceM = 0 #ultrasonicDistance(TRIGM, ECHOM)
        distanceR = 0 #ultrasonicDistance(TRIGR, ECHOR)
        

        print(f"Left Distance: {distanceL} cm, Middle Distance: {distanceM} cm, Right Distance: {distanceR} cm")
       
        
        #speedLeft = distanceM*0.005+0.5  # Adjust speed based on distance
       

        
except KeyboardInterrupt:
    GPIO.cleanup()

'''import RPi.GPIO as GPIO
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

try:
    while True:
        GPIO.output(TRIGL, False)
        time.sleep(0.5)
        
        GPIO.output(TRIGL, True)
        time.sleep(0.00001)
        GPIO.output(TRIGL, False)
        
        pulse_startL = time.time()
        while GPIO.input(ECHOL) == 0:
            pulse_startL = time.time()
            
        pulse_endL = time.time()
        while GPIO.input(ECHOL) == 1:
            pulse_endL = time.time()
        pulse_durationL = pulse_endL - pulse_startL
        distanceL = round(pulse_durationL * 17150,3)
        
        print(f"Distance: {distanceL} cm")

        speedLeft = distanceL*0.005+0.45  # Adjust speed based on distance
        if distanceL > 10 and distanceL < 100:
            speedLeft = distanceL*0.005+0.45
            leftMotor.forward(speedLeft)
            rightMotor.forward(speedLeft)
        elif distanceL <= 10 and distanceL > 8:
            speedLeft = 0
            leftMotor.forward(speedLeft)
            rightMotor.forward(speedLeft)
        elif distanceL <= 8:
            speedLeft = .25
            leftMotor.backward(speedLeft)
            rightMotor.backward(speedLeft)
            time.sleep(.1)
        else:
            leftMotor.forward(0)
            rightMotor.forward(0)
        
        
except KeyboardInterrupt:
    GPIO.cleanup()'''