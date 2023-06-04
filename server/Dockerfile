FROM ubuntu:22.04

RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install libopencv-dev python3-opencv python3-pip -qq
RUN apt-get install nodejs npm -qq
RUN npm i -g nodemon
RUN pip3 install flask flask_socketio gevent gevent-websocket numpy

WORKDIR /app

ENTRYPOINT [ "nodemon", "--exec", "python3", "opencv.py" ]