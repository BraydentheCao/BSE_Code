from flask import Flask, Response, render_template_string
import time, socket, math, json, queue, threading, cv2
import numpy as numpy
import mediapipe as mp

"""
This code is run on my computer, the TCPServer.py code is run on my raspberry pi. (The raspberry
pi is the server, my computer is the client)

This Flask application captures live video from a webcam and uses MediaPipe Hands to detect and 
analyze hand gestures in real time. It calculates the relative length and angle of the index 
finger compared to a reference finger segment, then sends this data as JSON to a separate server 
(my raspberry pi) via a TCP socket running on a specified IP and port. The app streams the video 
frames to a web client, allowing live viewing of hand tracking with MediaPipe's visual landmarks 
(points). Threading and queues manage asynchronous sending of gesture data to the server.
"""

"""
  ______                                                 __                         
 /      \                                               /  |                        
/$$$$$$  |  ______   _____  ____    ______   __    __  _$$ |_     ______    ______  
$$ |  $$/  /      \ /     \/    \  /      \ /  |  /  |/ $$   |   /      \  /      \ 
$$ |      /$$$$$$  |$$$$$$ $$$$  |/$$$$$$  |$$ |  $$ |$$$$$$/   /$$$$$$  |/$$$$$$  |
$$ |   __ $$ |  $$ |$$ | $$ | $$ |$$ |  $$ |$$ |  $$ |  $$ | __ $$    $$ |$$ |  $$/ 
$$ \__/  |$$ \__$$ |$$ | $$ | $$ |$$ |__$$ |$$ \__$$ |  $$ |/  |$$$$$$$$/ $$ |      
$$    $$/ $$    $$/ $$ | $$ | $$ |$$    $$/ $$    $$/   $$  $$/ $$       |$$ |      
 $$$$$$/   $$$$$$/  $$/  $$/  $$/ $$$$$$$/   $$$$$$/     $$$$/   $$$$$$$/ $$/       
                                  $$ |                                              
                                  $$ |                                              
                                  $$/                                               
"""

HOST = "192.168.68.82"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

app = Flask(__name__)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
cap = cv2.VideoCapture(0)
data_queue = queue.Queue()
frameCounter = 0
handOutFrameCounter = 0
buffer = b""

def socket_client_thread():
    global buffer
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        while True:
            message = data_queue.get()  # waits until data is available
            if message is None:
                break  # signal to shut down
            try:
                json_message = json.dumps(message).encode('utf-8')
                s.sendall(json_message)
                print("sent the msg")
                
                ack = s.recv(1024)
                print(f"[SOCKET] ACK received:")
                
                """
                buffer += ack

                decoded = buffer.decode("utf-8")
                message = json.loads(decoded)

                # Extract values
                relativeLength = message["relativeLength"]
                angleIndex = message["angleIndex"]

                print(f"Received Relative Length: {relativeLength:.3f}")
                print(f"Received Angle Index: {angleIndex:.3f}")
                """

                buffer = b""
            except Exception as e:
                print(f"[SOCKET ERROR] {e}")

threading.Thread(target=socket_client_thread, daemon=True).start()


def analyze_finger(base,tip,height,width):
    x = - (tip.x - base.x) * width
    y = (base.y - tip.y) * height # Flipped because of Open CV coordinate system

    #print(f"x = {x}")
    #print(f"y = {y}")

    angle = math.degrees(math.atan2(x,y))
    length = math.sqrt(x*x + y*y)

    return length, angle

def gen_frames():
    global frameCounter # This is check how much this will lag behind
    while True:
        frameCounter += 1
        handOutFrameCounter = 0
        success, frame = cap.read()
        if not success:
            break

        h, w, _ = frame.shape
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)
        
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks: # Draw hands
                mp.solutions.drawing_utils.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            hand = results.multi_hand_landmarks[0]
            five = hand.landmark[5]
            eight = hand.landmark[8]
            zero = hand.landmark[0]
            
            #time.sleep(0.25) # To slow the frame rate

            lengthIndex, angleIndex = analyze_finger(five,eight,h,w)
            lengthReference, _ = analyze_finger(zero,five,h,w)
            relativeLength = lengthIndex / lengthReference # Calculate by relative size

            print(f"Relative length: {relativeLength:.3f}")
            print(f"Angle: {angleIndex:.3f}")
            #print(f"Length: {lengthIndex}")
            
            """
            while not data_queue.empty():
                try:
                    data_queue.get_nowait()
                except queue.Empty:
                    break
            """
            # Create and send JSON message
            
            data_queue.put({
                "relativeLength": relativeLength,
                "angleIndex": angleIndex,
                "frameCounter": frameCounter
            })
        else:
            
            # If the hand has been out of frame long enough, then return 0 for all values. That should stop the robot
            data_queue.put({
                    "relativeLength": 0,
                    "angleIndex": 0,
                    "frameCounter": frameCounter
                })
            

            """
            handOutFrameCounter += 1
            frameCounter += 1
            if handOutFrameCounter > 5:
                data_queue.put({
                    "relativeLength": 0,
                    "angleIndex": 0,
                    "frameCounter": frameCounter
                })
            """

            
            
        frame = cv2.flip(frame, 1)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()  # Convert NumPy array to raw bytes

        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host='0.0.0.0')




