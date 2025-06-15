from pydantic import BaseModel, field_validator
from main.schemas.responses import DefaultResponse
from fastapi import HTTPException


class FactorUpdateDetail(BaseModel):
    factor_id: int
    weight_factor: int


class FactorUpdate(BaseModel):
    details: list[FactorUpdateDetail]

    @field_validator('details')
    def check_details_factors_(cls, details_: list[FactorUpdateDetail]):
        sum_details_factors = sum(item.weight_factor for item in details_)

        if sum_details_factors > 100:
            raise HTTPException(
                status_code=400,
                detail={
                    'result': False,
                    'message': f'Сумма весовых коэффициентов факторов не должна превышать 100%! '
                               f'Текущая сумма весовых коэффициентов = {sum_details_factors}%.',
                    'data': {}
                }
            )

        if sum_details_factors < 100:
            raise HTTPException(
                status_code=400,
                detail={
                    'result': False,
                    'message': f'Сумма весовых коэффициентов факторов должна составлять 100%! '
                               f'Текущая сумма весовых коэффициентов = {sum_details_factors}%.',
                    'data': {}
                }
            )

        return details_


class FactorRegular(BaseModel):
    factor_id: int
    name: str
    weight_factor: int


class FactorDefault(DefaultResponse):
    data: FactorRegular | tuple[FactorRegular] | tuple
