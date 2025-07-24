from flask import Flask, Response, render_template_string
import cv2, time, math, socket, json
import numpy as numpy

"""
 _______                                                 __ 
/       \                                               /  |
$$$$$$$  |  ______    _______   ______          ______  $$/ 
$$ |__$$ | /      \  /       | /      \        /      \ /  |
$$    $$<  $$$$$$  |/$$$$$$$/ /$$$$$$  |      /$$$$$$  |$$ |
$$$$$$$  | /    $$ |$$      \ $$ |  $$ |      $$ |  $$ |$$ |
$$ |  $$ |/$$$$$$$ | $$$$$$  |$$ |__$$ |      $$ |__$$ |$$ |
$$ |  $$ |$$    $$ |/     $$/ $$    $$/       $$    $$/ $$ |
$$/   $$/  $$$$$$$/ $$$$$$$/  $$$$$$$/        $$$$$$$/  $$/ 
                              $$ |            $$ |          
                              $$ |            $$ |          
                              $$/             $$/           
"""

HOST = ""  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Waiting for connection on port {PORT}...")
    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        buffer = b""
        while True:
            data = conn.recv(1024)
            if not data:
                break
            buffer += data

            try:
                # Try to decode a full JSON message
                decoded = buffer.decode("utf-8")
                message = json.loads(decoded)

                # Extract values
                relativeLength = message["relativeLength"]
                angleIndex = message["angleIndex"]
                frameCounter = message["frameCounter"]

                print(f"Relative Length: {relativeLength:.3f}")
                print(f"Angle Index: {angleIndex:.3f}")
                print(f"Frame counter: {frameCounter:.3f}")

                # Send an acknowledgment (optional)

                response = {
                    "angleIndex": angleIndex,
                    "relativeLength": relativeLength,
                }
                response_bytes = json.dumps(response).encode("utf-8")
                conn.sendall(response_bytes)
                

                buffer = b""  # Clear buffer for next message
            except json.JSONDecodeError:
                # Partial message received, wait for more data
                continue

