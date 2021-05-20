# coding=utf-8
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import SQL_CONNECT_ARGS, SQL_POOL_SIZE, SQL_POOL_TIMEOUT, SQL_URL

""" 实例化各种扩展，包括flask插件，也包括其他的一些实例，比如redis、minio、普罗米修斯等等 """
engine = create_engine(SQL_URL, pool_size=SQL_POOL_SIZE, pool_timeout=SQL_POOL_TIMEOUT, encoding='utf8', connect_args=SQL_CONNECT_ARGS)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)
