# coding=utf-8
import os
import shutil
from logging import getLogger

from config import IMAGE_PATH
from utils.time import timer

logger = getLogger(__name__)

"""####################################### INTERFACE WITH LOCAL #######################################"""


@timer
def post_file_to_storage(name, data):
    name = f'{IMAGE_PATH}{name}'
    if hasattr(data, 'read'):
        byte_data = data.read()
    elif hasattr(data, '__iter__'):
        byte_data = data
    else:
        raise Exception()
    with open(name, 'wb') as f:
        f.write(byte_data)
    logger.info(f'save {len(byte_data) // 1024} kb data, name: {name}')
    return name


@timer
def get_file_from_storage(name):
    with open(name, 'rb') as f:
        byte_data = f.read()
    logger.info(f'save {len(byte_data) // 1024} kb data, name: {name}')
    return byte_data


def rename_file(old_name, new_name):
    os.rename(old_name, new_name)


@timer
def copy_file(target: str, file):
    with open(target, "wb") as buffer:
        shutil.copyfileobj(file, buffer)
