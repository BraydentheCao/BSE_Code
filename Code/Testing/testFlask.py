from flask import Flask, Response
from picamera2 import Picamera2
import cv2
import numpy as np

app = Flask(__name__)

# Initialize camera
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (640, 480)}))
picam2.start()

# Generator to yield video frames
def generate_frames():
    while True:
        frame = picam2.capture_array()
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        # Yield the frame as an HTTP multipart response
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
def generate_filtered_frames():
    while True:
        frame = picam2.capture_array()
        # ret, buffer = cv2.imencode('.jpg', frame)
        
        hsv = cv2.cvtColor(frame,cv2.COLOR_RGB2HSV)
        # frame = buffer.tobytes()

        center = (frame.shape[0] // 2, frame.shape[1] // 2)
        print("HSV at center:", hsv[center[0], center[1]])

        lower_red1 = np.array([0, 80, 80])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([160, 80, 80])
        upper_red2 = np.array([179, 255, 255])

        

        cv2.imwrite("hsv.jpg", hsv)

        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

        result = cv2.bitwise_or(mask1, mask2)

        result = cv2.erode(result, None, iterations=2)
        result = cv2.dilate(result, None, iterations=2)
        
        result = cv2.cvtColor(result, cv2.COLOR_GRAY2RGB)

        ret, result = cv2.imencode('.jpg', result)
        
        result = result.tobytes()

        # Save to file

        # cv2.imwrite("result.jpg", result)

        # Yield the frame as an HTTP multipart response
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + result + b'\r\n')

# Route for video stream
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_filtered')
def video_filtered():
    return Response(generate_filtered_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Homepage just shows the video
@app.route('/')
def index():
    return '''
        <html>
            <head>
                <title>Pi Camera Dual Stream</title>
            </head>
            <body>
                <h1>Original Stream</h1>
                <img src="/video_feed" width="640"><br><br>

                <h1>Filtered Stream (Grayscale)</h1>
                <img src="/video_filtered" width="640">
            </body>
        </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)