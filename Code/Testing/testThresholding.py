
from picamera2 import Picamera2
import cv2
import numpy as np
import time
import matplotlib.pyplot as plt

#plt.plot([1, 2, 3], [4, 5, 6])
#plt.show()
#import cv2
#import numpy as np

img = 255 * np.ones((200, 200, 3), dtype=np.uint8)

cv2.imshow("Test", img)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Initialize and configure the camera
'''picam2 = Picamera2()
picam2.preview_configuration.main.size = (640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")
picam2.start()



time.sleep(.5)


# Capture one frame
frame = picam2.capture_array()

# Convert from RGB to BGR for OpenCV compatibility
# frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

# Save to file
cv2.imwrite("image.jpg", frame)

print("Frame saved as image.jpg")


# Load image in grayscale
image = cv2.imread("image.jpg", cv2.IMREAD_GRAYSCALE)

# Check if image was loaded
if image is None:
    print("Image not found.")
    exit()

# Apply thresholding
threshold_value = 127
_, thresh = cv2.threshold(image, threshold_value, 255, cv2.THRESH_BINARY)





# Show original and thresholded image
cv2.imshow("Original", image)
cv2.imshow("Thresholded", thresh)


picam2.close()
cv2.waitKey(0)
cv2.destroyAllWindows()

'''