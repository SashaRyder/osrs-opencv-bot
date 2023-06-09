from typing import List
import gevent
import gevent.monkey
gevent.monkey.patch_all(sys=True)

import cv2
from flask import Flask, render_template, Response, request
from flask_socketio import SocketIO, emit
import numpy as np
from utils.template_matches import template_matches
from bot_client import BotClient
from cv_template import CVTemplate
import glob
import functools
print = functools.partial(print, flush=True)

is_mining_template = CVTemplate("./functions/motherlode_mine/is_mining.png")
invent_full_template = CVTemplate("./functions/motherlode_mine/invent_full.png")
pickaxe_templates = list(map(lambda template: CVTemplate(template), glob.glob("./functions/motherlode_mine/pickaxes/*")))

botClients: List[BotClient] = list()

app = Flask(__name__, template_folder='./flask_html_templates')
socketio = SocketIO(app, max_http_buffer_size=5000000)

last_buffer: bytes

print("Running OpenCV OSRS Bot")
print("OPENCV VERSION: " + cv2.__version__)

@socketio.on('connect', namespace="/osrs")
def handle_connect():
    global botClients
    newBotClient = BotClient(request.sid)
    botClients.append(newBotClient)
    print("New Bot Connected, ID: " + newBotClient.id)
    emit("registration", newBotClient.id)

@socketio.on('task', namespace="/osrs")
def handle_message(task: str):
    global botClients
    thisClient: BotClient = next(filter(lambda client: client.id == request.sid, botClients), None)
    thisClient.set_task(task)
    emit("task_result", True)

@socketio.on('message', namespace="/osrs")
def handle_message(data: bytes):
    global last_buffer
    last_buffer = data

@socketio.on('disconnect', namespace="/osrs")
def handle_disconnect():
     print("BYE DISCONNECT")



def gen():    

    while True:
        gevent.sleep(0.05)
        imgbuff = np.frombuffer(last_buffer, dtype=np.uint8)
        openCvImage = cv2.imdecode(imgbuff, cv2.IMREAD_COLOR)
        mining_matches = template_matches(is_mining_template.get_template(), openCvImage)
        invent_full_matches = template_matches(invent_full_template.get_template(), openCvImage)
        if(len(list(invent_full_matches)) > 0):
            openCvImage = cv2.putText(openCvImage, "INVENTORY FULL", org=(50, 50), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=1, color=(255, 0, 0),thickness=1)
        mining_locations = []
        for template in pickaxe_templates: #Type: CVTemplate
            pickaxe_matches = template_matches(template.get_template(), openCvImage, 0.8)
            mining_locations += pickaxe_matches
            for locs in mining_locations:
                cv2.rectangle(openCvImage, locs, (locs[0] + template.get_width(), locs[1] + template.get_height()), (0,0,0), 2)
        for match in mining_matches:
            cv2.rectangle(openCvImage, match, (match[0] + is_mining_template.get_width(), match[1] + is_mining_template.get_height()), (0,0,0), 2)
        h, w = openCvImage.shape[:-1]
        if len(mining_locations) > 0:
            nearest_kp = min(mining_locations, key=lambda kp: np.linalg.norm(kp - np.array([ w/ 2, h / 2])))
            cv2.rectangle(openCvImage, nearest_kp, (nearest_kp[0] + template.get_width(), nearest_kp[1] + template.get_height()), (0,0,255), 2)
        _, buffer = cv2.imencode('.jpg', openCvImage)
        yield (b'--frame\r\n'
           b'Content-Type: image/jpeg\r\n\r\n' + bytes(buffer) + b'\r\n')


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
    socketio.run(app, host='0.0.0.0', debug=True, log_output=True, use_reloader=False)