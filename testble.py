from datetime import datetime
from typing import Iterator
import uvicorn
import serial
import cv2
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.responses import Response
import sys
import time
import serial
import numpy as np
import cv2
import json
import logging
import sys
import asyncio
import RPi.GPIO as GPIO
import time
from RpiMotorLib import RpiMotorLib

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

serialPort = serial.Serial(port='/dev/rfcomm0', baudrate=115200, timeout=0, parity=serial.PARITY_EVEN, stopbits=1)
size = 4096

GpioPins = [18, 23, 24, 25]

camera = cv2.VideoCapture(0)

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
# Declare a named instance of class pass a name and motor type
mymotortest = RpiMotorLib.BYJMotor("MyMotorOne", "28BYJ")

class CircularList(list):

  def __init__(self, data, maxlen=0):
    assert isinstance(data, list), "Invalid data. It must be a list."

    # zero-pad or trim data from the left to fit to maximum length
    maxlen = len(data) if(maxlen == 0) else maxlen
    delta = maxlen - len(data)
    if(delta > 0):
      data = [0]*delta + data # prepend zeros
    else:
      data[:-maxlen] = []     # trim the leftmost portion

    # initialize the parent list constructor with the data
    super().__init__(data)

  def add(self, data):
    # convert to iterable (list) if just a single number
    data = data if isinstance(data, list) else [data]


    # shift the array if the shift is less than array length
    shift = len(data)
    maxlen = len(self)
    if(shift < maxlen):
      self[:-shift] = self[shift:] # shift the existing data left
      self[-shift:] = data         # append the new data to the end
    else:
      self[:] = data[-maxlen:]     # only copy the rightmost portion

  def clear(self):
   self.add([0]*len(self))





async def generate_random_data(request: Request) -> Iterator[str]:
    """
    Gets data from the connected bluetooth device

    :return: String containing current timestamp (YYYY-mm-dd HH:MM:SS) and data gathered from the bluetooth.
    """
    last_50_samples_data1 = CircularList([],maxlen=20)
    last_50_samples_data2 = CircularList([],maxlen=20)
    client_ip = request.client.host
    logger.info("Client %s connected", client_ip)
    while True:
        try:
            data = serialPort.readline()
            if data:
                data = data.decode("utf-8")
                newdata = data.split(" ")
                newdata[1] = newdata[1].replace("\r\n", "")
            json_data = json.dumps(
                {
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "value1": newdata[0],
                    "value2": newdata[1]
                }
            )
            yield f"data:{json_data}\n\n"
        except:
            continue
        last_50_samples_data1.add(float(newdata[0]))
        last_50_samples_data2.add(float(newdata[1]))

        # Get average of last 50 samples
        avg_data1 = sum(last_50_samples_data1) / len(last_50_samples_data1)
        avg_data2 = sum(last_50_samples_data2) / len(last_50_samples_data2)

        # Get the difference between the average and the current value
        diff_data1 = avg_data1 - float(newdata[0])
        diff_data2 = avg_data2 - float(newdata[1])
        if(20 > abs(diff_data1) > 0.15):
            print(diff_data1)
            move_left()
        elif(20 > abs(diff_data2) > 0.15):
            print(diff_data2)
            move_right()
        await asyncio.sleep(0.1)

def move_left():
    mymotortest.motor_run(GpioPins , .002, 5, True, False, "full", .05)
def move_right():
    mymotortest.motor_run(GpioPins , .002, 5, False, False, "full", .05)

def gen_frames():
    while True:
        success, frame = camera.read()
        
        if not success:
            break
        else:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Face detection using Haar cascades
            face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

            # Detect faces
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            img_faces = frame.copy()

            # Draw the faces on the original imIage
            for (x, y, w, h) in faces:
                cv2.rectangle(img_faces, (x, y), (x+w, y+h), (255, 0, 0), 2)


            cv2.normalize(frame, frame, 50, 255, cv2.NORM_MINMAX)
            frame = cv2.flip(img_faces, 0)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


application = FastAPI()
templates = Jinja2Templates(directory="templates")
application.mount("/public", StaticFiles(directory="public"), name="public")

application.mount("/assets", StaticFiles(directory="assets"), name="assets")

@application.get("/", response_class=HTMLResponse)
async def index(request: Request) -> Response:
    return templates.TemplateResponse("index.html", {"request": request})

@application.get('/video_feed')
async def video_feed():
    return StreamingResponse(gen_frames(), media_type='multipart/x-mixed-replace; boundary=frame')

@application.get('/chart-data')
async def chart_data(request: Request) -> StreamingResponse:
    response = StreamingResponse(generate_random_data(request), media_type="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    return response
    
if __name__ == '__main__':
    uvicorn.run(application, host='0.0.0.0', port=6543)
