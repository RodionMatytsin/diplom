from fastapi import HTTPException
from pydantic import BaseModel, field_validator
from main.utils.validation import check_class


class ClassAdd(BaseModel):
    name_class: str

    @field_validator('name_class')
    def check_role_(cls, name_class_):
        name_class_ = check_class(name_class_=name_class_)
        if not name_class_:
            raise HTTPException(
                status_code=400,
                detail={'result': False, 'message': 'Поле «Название класса» введено некорректно!', 'data': {}}
            )
        return name_class_
