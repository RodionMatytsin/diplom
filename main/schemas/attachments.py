from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class AttachmentRegular(BaseModel):
    guid: UUID | str
    type: str
    url: str
    path: str
    datetime: datetime


class AttachmentDefault(BaseModel):
    guid: UUID | str
    type: str
    url: str
