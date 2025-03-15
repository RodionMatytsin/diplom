from pydantic import BaseModel
from typing import Any


class RequestJsonLogSchema(BaseModel):
    """
    Схема части запросов лога в формате JSON
    """
    method: str
    uri: str
    path: str

    query: str
    body: str
    size: int

    headers: str
    cookie: str

    remote_ip: str | None = None
    remote_port: int | str | None = None


class ResponseJsonLogSchema(BaseModel):
    """
    Схема части ответов лога в формате JSON
    """
    status_code: int
    body: str
    header: str
    size: int


class Service(BaseModel):
    id: str
    name: str
    version: str


class Log(BaseModel):
    level: int
    level_name: str
    message: str | None = None
    exceptions: str | None = None
    source: str | None = None
    thread: str | int | None = None


class BaseJsonLogSchema(BaseModel):
    """
    Схема части запросов-ответов лога в формате JSON
    """
    service: Service | None = None
    log: Log | None = None
    request: RequestJsonLogSchema | None = None
    response: ResponseJsonLogSchema | None = None

    duration: float | int | None = None
    timestamp: Any | None = None

    class Config:
        populate_by_name = True
