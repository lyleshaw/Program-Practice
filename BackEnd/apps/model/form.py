from sqlalchemy import Column, Integer, Boolean, VARCHAR, SMALLINT, text

from apps.a_common.db import Base


class FormDB(Base):
    __tablename__ = 'form'
    
    id = Column(Integer(), primary_key=True)
    name = Column(VARCHAR(126), nullable=False)
    sex = Column(SMALLINT)
    phone = Column(VARCHAR(126))
    IDCard = Column(VARCHAR(126))
    org_name = Column(VARCHAR(126))
    car_id = Column(VARCHAR(126))
    reason = Column(VARCHAR(126))
    guarantor = Column(VARCHAR(126))
    guarantor_phone = Column(VARCHAR(126))
    health_code_status = Column(Integer, default=0)
    is_been_epidemic_area_in_two_weeks = Column(Boolean, server_default=text('False'))
    is_cough = Column(Boolean, server_default=text('False'))
    in_time_applied = Column(Integer)
    out_time_applied = Column(Integer)
    in_time_real = Column(Integer)
    out_time_real = Column(Integer)
