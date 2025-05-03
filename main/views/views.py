from main import main, templates
from fastapi import Request
from fastapi.responses import HTMLResponse


@main.get("/", response_class=HTMLResponse, status_code=200, tags=["Views"])
async def index(request: Request):
    return templates.TemplateResponse("index.html", context={"request": request})


@main.get("/schoolchildren", response_class=HTMLResponse, status_code=200, tags=["Views"])
async def schoolchildren(request: Request):
    return templates.TemplateResponse("schoolchildren.html", context={"request": request})
