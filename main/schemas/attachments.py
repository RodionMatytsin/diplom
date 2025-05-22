from pydantic import BaseModel
from datetime import datetime


class AttachmentRegular(BaseModel):
    guid: str
    type: str
    url: str
    path: str
    datetime: datetime


class AttachmentDefault(BaseModel):
    guid: str
    type: str
    url: str
