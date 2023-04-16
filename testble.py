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

async def generate_random_data(request: Request) -> Iterator[str]:
    """
    Gets data from the connected bluetooth device

    :return: String containing current timestamp (YYYY-mm-dd HH:MM:SS) and data gathered from the bluetooth.
    """
    client_ip = request.client.host
    logger.info("Client %s connected", client_ip)
    while True:
        try:
            data = serialPort.readline()
            if data:
                data = data.decode("utf-8")
                newdata = data.split(" ")
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
        avgdata1 =
        avgdata2 = 
        await asyncio.sleep(0.1)

async def move_left():
    for i in range(50):
        mymotortest.motor_run(GpioPins , .002, 5, True, False, "full", .05)

async def move_right():
    for i in range(50):
        mymotortest.motor_run(GpioPins , .002, 5, False, False, "full", .05)

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
