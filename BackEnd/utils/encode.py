import binascii
import datetime
import decimal
import hashlib
from json import JSONEncoder
from random import SystemRandom
from uuid import UUID, uuid4 as _uuid4


def uuid():
    return _uuid4().hex


def _get_duration_components(duration):
    days = duration.days
    seconds = duration.seconds
    microseconds = duration.microseconds
    
    minutes = seconds // 60
    seconds = seconds % 60
    
    hours = minutes // 60
    minutes = minutes % 60
    
    return days, hours, minutes, seconds, microseconds


def duration_iso_string(duration):
    if duration < datetime.timedelta(0):
        sign = '-'
        duration *= -1
    else:
        sign = ''
    
    days, hours, minutes, seconds, microseconds = _get_duration_components(
        duration)
    ms = '.{:06d}'.format(microseconds) if microseconds else ""
    return '{}P{}DT{:02d}H{:02d}M{:02d}{}S'.format(sign, days, hours, minutes,
                                                   seconds, ms)


class MyJSONEncoder(JSONEncoder):
    def default(self, o):
        # See "Date Time String Format" in the ECMA-262 specification.
        if isinstance(o, datetime.datetime):
            r = o.isoformat()
            if o.microsecond:
                r = r[:23] + r[26:]
            if r.endswith('+00:00'):
                r = r[:-6] + 'Z'
            return r
        elif isinstance(o, datetime.date):
            return o.isoformat()
        elif isinstance(o, datetime.time):
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r
        elif isinstance(o, datetime.timedelta):
            return duration_iso_string(o)
        elif isinstance(o, decimal.Decimal):
            return str(round(o, 2))
        elif isinstance(o, UUID):
            return str(o)
        else:
            return super().default(o)


json = MyJSONEncoder()

_sys_rng = SystemRandom()
SALT_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
DEFAULT_PBKDF2_ITERATIONS = 150000
HASH_NAME = 'sha256'
METHOD_NAME = f'pbkdf2:{HASH_NAME}:{DEFAULT_PBKDF2_ITERATIONS}'
SALT_LEN = 8


def gen_salt(length) -> str:
    if length <= 0:
        raise ValueError("Salt length must be positive")
    return "".join(_sys_rng.choice(SALT_CHARS) for _ in range(length))


def hash_password(pw: bytes, salt: bytes) -> str:
    h = hashlib.pbkdf2_hmac(HASH_NAME, pw, salt, 150000)
    return binascii.hexlify(h).decode('utf-8')


def generate_password_hash(pw: str) -> str:
    salt = gen_salt(SALT_LEN)
    h = hash_password(pw.encode('utf-8'), salt.encode())
    return "%s$%s$%s" % (METHOD_NAME, salt, h)


def is_right_password(pw: str, hashpw: str) -> bool:
    if hashpw.count("$") < 2:
        return False
    _, salt, hashval = hashpw.split("$", 2)
    h = hash_password(pw.encode('utf-8'), salt.encode())
    return h == hashval


def get_birthday_by_IDCard(id: str) -> datetime.datetime:
    """通过身份证号获取出生日期"""
    birth_year = int(id[6:10])
    birth_month = int(id[10:12])
    birth_day = int(id[12:14])
    
    return datetime.datetime(year=birth_year, month=birth_month, day=birth_day)
