from logging import Filter, Formatter, getLogger, INFO, LogRecord, StreamHandler, WARNING
from logging.handlers import TimedRotatingFileHandler

try:
    from config import LOG_LEVEL, LOG_FILE, HB_LOG_FILE, TASK_LOG, SQL_LOG
except ImportError:
    LOG_LEVEL, LOG_FILE, HB_LOG_FILE, TASK_LOG, SQL_LOG = INFO, '/log/web/view.log', '/log/web/hb-view.log', '/log/web/task.log', '/log/web/sql.log'


class RequestIdFilter(Filter):
    def filter(self, record: LogRecord):
        record.request_id = "request_id"
        return True


formatter = Formatter(
    # '[%(asctime)s].[%(msecs)s] [%(levelname)s] [%(name)s]:[%(filename)s]:[%(funcName)-6s]:[%(request_id)s] %(message)s'
    '[%(asctime)s] [%(name)s]:[%(funcName)-6s]:[%(levelname)s] : %(message)s'
)


def init_logger_config():
    init_common_log()
    init_sql_log()


def init_common_log():
    logger1 = getLogger('apps')
    logger2 = getLogger('utils')
    
    if LOG_FILE:
        logger1.setLevel(LOG_LEVEL)
        logger2.setLevel(LOG_LEVEL)
        handler = TimedRotatingFileHandler(filename=LOG_FILE, when='D', interval=2, encoding="utf-8")
        handler.setFormatter(formatter)
        logger1.addHandler(handler)
        logger2.addHandler(handler)
    else:
        logger1.setLevel(INFO)
        logger2.setLevel(INFO)
        handler = StreamHandler()
        handler.setFormatter(formatter)
        logger1.addHandler(handler)
        logger2.addHandler(handler)


def init_sql_log():
    logger = getLogger("sqlalchemy.orm")
    logger.setLevel(WARNING)
    
    logger = getLogger("sqlalchemy.engine")
    if SQL_LOG:
        logger.setLevel(LOG_LEVEL)
        handler = TimedRotatingFileHandler(filename=SQL_LOG, when='D', interval=2, encoding="utf-8")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    else:
        logger.setLevel(INFO)
        handler = StreamHandler()
        handler.setFormatter(formatter)
        logger.handlers = []
        logger.addHandler(handler)


def set_all_log_info(l):
    getLogger('apps').setLevel(l)
    getLogger('utils').setLevel(l)
    getLogger("sqlalchemy").setLevel(l)

# init_logger_config()
