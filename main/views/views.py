from main import main, templates
from fastapi import Request
from fastapi.responses import HTMLResponse


@main.get("/", response_class=HTMLResponse, status_code=200, tags=["Views"])
async def index(request: Request):
    return templates.TemplateResponse("index.html", context={"request": request})
