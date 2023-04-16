# Necessary Imports
from fastapi.responses import RedirectResponse
from fastapi import FastAPI                   # The main FastAPI import
from fastapi.responses import HTMLResponse    # Used for returning HTML responses
from fastapi.staticfiles import StaticFiles   # Used for serving static files
import uvicorn                                # Used for running the app
from fastapi import FastAPI, Request, Form
from urllib.request import urlopen
import json

app = FastAPI()

# Mount static directories
app.mount("/public", StaticFiles(directory="public"), name="public")
app.mount("/assets", StaticFiles(directory="assets"), name="assets")
@app.get("/", response_class = HTMLResponse)
def get_html() -> HTMLResponse:
    with open("index.html") as html:
        return HTMLResponse(content=html.read())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=6523)

