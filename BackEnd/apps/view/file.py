import os
from typing import List

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import FileResponse

from apps.a_common.error import NotFound
from apps.a_common.response import error_response
from apps.a_common.storage import get_filename_without_uuid_prefix, make_file_url, save_as_temp_file

file_router = APIRouter()
file_prefix = 'files'


@file_router.get("/{file_path:path}", summary="下载文件")
async def get_file(file_path: str):
    if not os.path.exists(file_path):
        return error_response(NotFound())
    return FileResponse(path=file_path, filename=get_filename_without_uuid_prefix(file_path))


@file_router.post("", summary="上传文件")
async def post_file(files: List[UploadFile] = File(...)):
    result = []
    for file in files:
        path = save_as_temp_file(file)
        result.append({
            'url': make_file_url(path),
            'file_address': path
        })
    return result
