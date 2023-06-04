from gevent import monkey
import gevent
monkey.patch_all()

from threading import Thread
import time
import cv2
import os
from flask import Flask, render_template,Response
from flask_socketio import SocketIO
import base64
import numpy as np
from utils.template_matches import template_matches
from cv_template import cv_template

import functools
print = functools.partial(print, flush=True)

is_mining_template = cv_template("./cv_templates/mining/is_mining.png")

app = Flask(__name__)
socketio = SocketIO(app, async_mode="gevent", max_http_buffer_size=5000000)

last_buffer = []

total_images = 0
run_start = time.time()

host_server = os.environ.get("RTSP_HOST")
print("Running OpenCV OSRS Bot")
print("OPENCV VERSION: " + cv2.__version__)

@socketio.on('connect', namespace="/osrs")
def handle_connect():
    print("HI CONNECTED")

@socketio.on('message', namespace="/osrs")
def handle_message(data):
    global last_buffer, total_images
    total_images += 1
    last_buffer = data

@socketio.on('disconnect', namespace="/osrs")
def handle_disconnect():
     print("BYE DISCONNECT")

def total_run_time_seconds() -> float:
    return time.time() - run_start



def gen():    

    while True:
        gevent.sleep(0.05)
        imgbuff = np.frombuffer(last_buffer, dtype=np.uint8)
        openCvImage = cv2.imdecode(imgbuff, cv2.IMREAD_COLOR)
        mining_matches = template_matches(is_mining_template.getTemplate(), openCvImage)
        for match in mining_matches:
            cv2.rectangle(openCvImage, match, (match[0] + is_mining_template.getHeight(), match[1] + is_mining_template.getWidth()), (0,0,255), 2)
        openCvImage = cv2.putText(openCvImage, str(round((total_images / total_run_time_seconds()))) + "fps", org=(50, 50), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=1, color=(0, 0, 0),thickness=1)
        _, buffer = cv2.imencode('.jpg', openCvImage)
        baseimage = base64.b64encode(buffer)
        yield (b'--frame\r\n'
           b'Content-Type: image/jpeg\r\n\r\n' + base64.decodebytes(baseimage) + b'\r\n')


@app.route('/')
def index():
    """Video streaming"""
    return render_template('./index.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    if(len(last_buffer) <= 0):
        return "No stream yet."
    return Response(gen(),
                mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True, log_output=True)