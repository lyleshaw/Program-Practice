from logging import getLogger

from itsdangerous import BadSignature, SignatureExpired, TimedJSONWebSignatureSerializer

from config import SECRET_KEY

logger = getLogger(__name__)
TIMEOUT = 60 * 60 * 31

s = TimedJSONWebSignatureSerializer(SECRET_KEY, expires_in=TIMEOUT)


def decode_token(token) -> (dict, bool):
    if isinstance(token, str):
        token = token.encode()
    
    try:
        return s.loads(token), True
    except BadSignature:
        logger.info('decode jwt fail, detail: {}'.format(token))
        return {}, False
    except SignatureExpired:
        logger.info('token expire')
        return {}, False
    except Exception as e:
        logger.error(f"unknown jwt decode error: {str(e)}")
        return {}, False


def encode_token(user_id) -> bytes:
    return s.dumps(user_id)
