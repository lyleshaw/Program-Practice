import json

import requests
from requests import ConnectTimeout, ReadTimeout, Response

from apps.a_common.error import NetworkError
from apps.foundation import log
from utils.time import timer


@timer
def request_twice_if_fail(url,
                          params=None,
                          header=None,
                          json=None,
                          files=None,
                          cookies=None,
                          method='get'):
    def raise_request_detail():
        log.warning(
            f'url {method.upper()} : {url}, header: {header}, params: {params}, json: {json}, cookies: {cookies}'
        )
        log.warning(f'response text: {response.text}')
        raise NetworkError(f'request {url} fail')
    
    request_dict = {
        'get': requests.get,
        'post': requests.post,
        'delete': requests.delete,
        'put': requests.put
    }
    # 确保发送完成, 发送请求两次
    log.info(f'try to request {method.upper()} : {url}')
    try:
        response = request_dict[method](url=url,
                                        headers=header,
                                        params=params,
                                        json=json,
                                        files=files,
                                        cookies=cookies,
                                        timeout=(2, 3))
    except (ReadTimeout, ConnectTimeout, ConnectionError, Exception):
        log.warning(
            f'url {method.upper()} : {url}, header: {header}, params: {params}, json: {json}'
        )
        response = request_dict[method](url=url,
                                        headers=header,
                                        params=params,
                                        json=json,
                                        files=files,
                                        cookies=cookies,
                                        timeout=(2, 5))
    
    # 根据约定判断请求是否成功
    if 'v2' in url and not check_v2_api_success(response):
        raise_request_detail()
    elif not check_http_success(response):
        raise_request_detail()
    
    return response


def check_http_success(response: Response):
    if response.status_code // 10 != 20:
        error_msg = 'Request Exception:{}\n'.format(
            ' status code is {}'.format(response.status_code))
        log.warning(error_msg)
        return False
    return True


def check_v2_api_success(response: Response):
    if not check_http_success(response):
        return False
    
    try:
        response_data = response.json()
    except json.JSONDecodeError as e:
        log.warning(f'the response content: {response.content}')
        return False
    except Exception as e:
        log.warning(
            f'get response json error, detail: {type(e)}, {e.args}, {response.content}'
        )
        return False
    else:
        if response_data['code'] != 200:
            log.warning(f'response api code != 200, detail: {response_data}')
            return False
    
    return True
