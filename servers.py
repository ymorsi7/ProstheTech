import uvicorn
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse, HTMLResponse
import serial
import datetime, psutil
import asyncio
from easycharts import ChartServer
from easyschedule import EasyScheduler

serialPort = serial.Serial(port='COM15', baudrate=115200, timeout=0, parity=serial.PARITY_EVEN, stopbits=1)
size = 4096

app = FastAPI()
scheduler = EasyScheduler()
templates = Jinja2Templates(directory="templates")

every_minute = '* * * * *'

@app.on_event('startup')
async def setup():
    asyncio.create_task(scheduler.start())
    app.charts = await ChartServer.create(
        app,
        charts_db="charts_database",
        chart_prefix = '/mycharts'
    )



@app.get('/')
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get('/data')
def video_feed(request: Request):
    
    while 1:
        data = serialPort.readline(size)
        if data:
            print(data)
    

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
