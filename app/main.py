import os

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .utils import get_result

app = FastAPI()
static_path = os.path.join(os.path.dirname(__file__), 'static/')
app.mount('/static', StaticFiles(directory=static_path), name='static')
templates = Jinja2Templates(directory='app')


@app.get('/', response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})


@app.post('/result')
async def result(request: Request):
    """Accept a playlist id and return the result from get_result()."""
    data = await request.json()
    playlist = data.get('playlist')
    result = await get_result(playlist)
    return result
