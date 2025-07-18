
from picamera2 import Picamera2
import cv2
import numpy as np
import time

# Initialize and configure the camera
picam2 = Picamera2()
picam2.preview_configuration.main.size = (640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")
picam2.start()

# cv2 represents hue values between 0 & 179 (red is 160 to 10)


time.sleep(.5)


# Capture one frame
frame = picam2.capture_array()

# Convert from RGB to BGR for OpenCV compatibility
# frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)

lower_red1 = np.array([0, 100, 100])
upper_red1 = np.array([10, 255, 255])
lower_red2 = np.array([160, 100, 100])
upper_red2 = np.array([179, 255, 255])


cv2.imwrite("hsv.jpg", hsv)

center = (frame.shape[0] // 2, frame.shape[1] // 2)
print("HSV at center:", hsv[center[0], center[1]])

mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
mask2 = cv2.inRange(hsv, lower_red2, upper_red2)



result = cv2.bitwise_or(mask1, mask2)

result = cv2.erode(result, None, iterations=2)
result = cv2.dilate(result, None, iterations=2)

# Save to file

cv2.imwrite("result.jpg", result)

print("Frame saved as result.jpg")
picam2.close()
cv2.destroyAllWindows()


'''
while True:
    frame = picam2.capture_array()

    # Convert to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)

    # Define color range for detection (e.g., red objects)
    lower_red = np.array([0, 100, 100])
    upper_red = np.array([10, 255, 255])

    # Create a mask and apply to original frame
    mask = cv2.inRange(hsv, lower_red, upper_red)
    result = cv2.bitwise_and(frame, frame, mask=mask)

    # Show frames
    # cv2.imshow("Original", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
    cv2.imwrite("output.jpg", cv2.cvtColor(result, cv2.COLOR_RGB2BGR))
    print("Saved output.jpg")

    # Break loop with 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
picam2.close()
cv2.destroyAllWindows()
'''