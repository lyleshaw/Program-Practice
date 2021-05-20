import re
from pathlib import Path

from fastapi import UploadFile

from config import ADDRESS, API_PREFIX, IMAGE_PATH
from utils.encode import uuid
from utils.storage import copy_file

pattern = re.compile(r'[0-9a-f]{32}')


def temp_file_name(filename: str) -> str:
    return f"{uuid()}_{filename}"


def save_as_temp_file(file: UploadFile) -> str:
    path = f"{IMAGE_PATH}{temp_file_name(file.filename)}"
    copy_file(path, file.file)
    return path


def get_filename_without_uuid_prefix(name: str) -> str:
    p = Path(name)
    t = p.name.split('_', 1)
    if len(t) == 2 and pattern.match(t[0]).end() == 32:
        return p.name[33:]
    return p.name


def make_file_url(path: str):
    return f"{ADDRESS}{API_PREFIX}/files/{path}"
