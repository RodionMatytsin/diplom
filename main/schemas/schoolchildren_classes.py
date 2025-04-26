from uuid import UUID
from pydantic import BaseModel
from main.schemas.responses import DefaultResponse


class SchoolchildrenClassRegular(BaseModel):
    guid: UUID | str
    name_class: str
    estimation: float | None


class SchoolchildrenClassDefault(DefaultResponse):
    data: SchoolchildrenClassRegular | tuple[SchoolchildrenClassRegular] | tuple
