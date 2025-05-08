from main import main, templates
from fastapi import Request
from fastapi.responses import HTMLResponse


@main.get("/", response_class=HTMLResponse, status_code=200, tags=["Views"])
async def index(request: Request):
    return templates.TemplateResponse("index.html", context={"request": request})


@main.get("/schoolchildren", response_class=HTMLResponse, status_code=200, tags=["Views"])
async def schoolchildren(request: Request):
    return templates.TemplateResponse("schoolchildren.html", context={"request": request})


@main.get("/teachers", response_class=HTMLResponse, status_code=200, tags=["Views"])
async def teachers(request: Request):
    return templates.TemplateResponse("teachers.html", context={"request": request})


@main.get("/admin/{secret_key}", response_class=HTMLResponse, status_code=200, tags=["Views"])
async def admin(secret_key: str, request: Request):
    from main.config import SECRET_KEY
    if secret_key != SECRET_KEY:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=403,
            detail={"result": False, "message": "У вас нет прав!", "data": {}}
        )
    return templates.TemplateResponse("admin.html", context={"request": request})
