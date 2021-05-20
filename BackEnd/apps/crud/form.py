from typing import List
from sqlalchemy.orm import Session, Query

from apps.model.form import FormDB
from apps.serializer.form import FormSerializer, FormSearchSerializer


def add_form(session: Session, form_data: FormSerializer) -> FormDB:
    form = FormDB(
        name=form_data.name,
        sex=form_data.sex,
        phone=form_data.phone,
        IDCard=form_data.IDCard,
        org_name=form_data.org_name,
        car_id=form_data.car_id,
        reason=form_data.reason,
        guarantor=form_data.guarantor,
        guarantor_phone=form_data.guarantor_phone,
        health_code_status=form_data.health_code_status,
        is_cough=form_data.is_cough,
        is_been_epidemic_area_in_two_weeks=form_data.is_been_epidemic_area_in_two_weeks,
        in_time_applied=form_data.in_time_applied,
        in_time_real=form_data.in_time_real,
        out_time_real=form_data.out_time_real,
        out_time_applied=form_data.out_time_applied)
    session.add(form)
    return form


def get_form_by_id(session: Session, form_id: int) -> FormDB:
    form = session.query(FormDB).filter(FormDB.id == form_id).first()
    return form


def get_form_by_search(session: Session, search_condiction: FormSearchSerializer) -> Query:
    query = session.query(FormDB)
    if search_condiction.name is not None:
        query.filter(FormDB.name == search_condiction.name)
    if search_condiction.sex is not None:
        query.filter(FormDB.sex == search_condiction.sex)
    if search_condiction.health_code_status is not None:
        query.filter(FormDB.health_code_status == search_condiction.health_code_status)
    if search_condiction.is_been_epidemic_area_in_two_weeks is not None:
        query.filter(FormDB.is_been_epidemic_area_in_two_weeks == search_condiction.is_been_epidemic_area_in_two_weeks)
    if search_condiction.is_cough is not None:
        query.filter(FormDB.is_cough == search_condiction.is_cough)
    if search_condiction.in_time is not None:
        query.filter(FormDB.in_time_real > search_condiction.in_time)
    if search_condiction.out_time is not None:
        query.filter(FormDB.out_time_real < search_condiction.out_time)
    return query


def delete_form_by_id(session: Session, form_id: int) -> FormDB:
    form = session.query(FormDB).filter(FormDB.id == form_id).first()
    session.delete(form)
    return form
