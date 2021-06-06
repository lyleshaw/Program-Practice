from typing import List
from pydantic import BaseModel

from apps.a_common.constants import SEX_LITERAL, HealthCode_Literal
from apps.a_common.scheme import PhoneField, IDCardField
from apps.model.form import FormDB


class FormSerializer(BaseModel):
    id: int = None
    name: str
    sex: SEX_LITERAL
    phone: str = PhoneField
    IDCard: str = IDCardField
    org_name: str
    car_id: str
    reason: str
    guarantor: str
    guarantor_phone: str
    health_code_status: HealthCode_Literal
    is_been_epidemic_area_in_two_weeks: bool
    is_cough: bool
    in_time_applied: int
    out_time_applied: int
    in_time_real: int
    out_time_real: int
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example":
                {
                    "sex": 1,
                    'name': '张三',
                    "phone": "13218655818",
                    "IDCard": "410503198801010031",
                    "org_name": "x大学党委组织部",
                    "car_id": "浙A88888",
                    "reason": "走亲访友",
                    "guarantor": "老王",
                    "guarantor_phone": "13218655818",
                    "health_code_status": 1,
                    "is_been_epidemic_area_in_two_weeks": 0,
                    "is_cough": 0,
                    "in_time_applied": 1621497617,
                    "out_time_applied": 1621497618,
                    "in_time_real": 1621497619,
                    "out_time_real": 1621497620
                }
        }


class FormUpdateSerializer(BaseModel):
    phone: str = PhoneField


class FormSearchSerializer(BaseModel):
    name: str = None
    sex: SEX_LITERAL = None
    health_code_status: HealthCode_Literal = None
    is_been_epidemic_area_in_two_weeks: bool = None
    is_cough: bool = None
    in_time: int = None
    out_time: int = None
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example":
                {
                    "sex": 1,
                    'name': '张三',
                    "health_code_status": 1,
                    "is_been_epidemic_area_in_two_weeks": 0,
                    "is_cough": 0,
                    "in_time": 0,
                    "out_time": 1721497618
                }
        }


def to_FormDetailSerializer(form: FormDB) -> dict:
    s = FormSerializer.from_orm(form)
    return s.dict()


def to_UserDetailSerializerList(forms: List[FormDB]) -> List[dict]:
    return [to_FormDetailSerializer(f) for f in forms]
