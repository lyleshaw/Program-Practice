from .error_code import ER


class AppError(RuntimeError):
    def __init__(self, error_record=ER.NOT_DEFINED, fields=None):
        super(AppError, self).__init__()
        self.code = error_record.code
        self.fields = fields
        self.detail = error_record.detail


"""##################################################################################################################
Common
##################################################################################################################"""


class NotFound(AppError):
    def __init__(self, fields=None):
        super(NotFound, self).__init__(error_record=ER.NOTFOUND, fields=fields)


class InvalidParamError(AppError):
    def __init__(self, fields=None):
        super(InvalidParamError,
              self).__init__(error_record=ER.MISS_REQUIRED_PARAM, fields=fields)


class PermissionError(AppError):
    def __init__(self, fields=None):
        super(PermissionError, self).__init__(error_record=ER.PERMISSION_ERROE,
                                              fields=fields)


class ResourceExistError(AppError):
    def __init__(self, fields=None):
        super(ResourceExistError,
              self).__init__(error_record=ER.RESOURCE_EXISTED_ERROR,
                             fields=fields)


class ResourceNotExistError(AppError):
    def __init__(self, fields=None):
        super(ResourceNotExistError,
              self).__init__(error_record=ER.RESOURCE_NOT_EXIST_ERROR, fields=fields)


class NeedRedirtError(AppError):
    def __init__(self, fields=None):
        super(NeedRedirtError,
              self).__init__(error_record=ER.NEED_REDIRT_ERROR, fields=fields)


class NetworkError(AppError):
    def __init__(self, fields=None):
        super(NetworkError, self).__init__(error_record=ER.NETWORK_ERROR, fields=fields)


class DBError(AppError):
    def __init__(self, fields=None):
        super(DBError, self).__init__(error_record=ER.DB_ERROR, fields=fields)


class NotLoginError(AppError):
    def __init__(self, fields=None):
        super(NotLoginError, self).__init__(error_record=ER.NOT_LOGIN, fields=fields)


class EmptyContent(AppError):
    def __init__(self, fields=None):
        super(EmptyContent, self).__init__(error_record=ER.EMPTY_CONTENT, fields=fields)


class RequestThrottled(AppError):
    def __init__(self, fields=None):
        super(RequestThrottled, self).__init__(error_record=ER.REQUEST_THROTTLED, fields=fields)


class PremissionDenied(AppError):
    def __init__(self, fields=None):
        super(PremissionDenied, self).__init__(error_record=ER.PERMISSION_DENIED, fields=fields)


class HasHandled(AppError):
    def __init__(self, fields=None):
        super(HasHandled, self).__init__(error_record=ER.HAS_HANDLED, fields=fields)


class WrongPassword(AppError):
    def __init__(self, fields=None):
        super(WrongPassword, self).__init__(error_record=ER.WRONG_PASSWORD, fields=fields)


class RepeatedId(AppError):
    def __init__(self, fields=None):
        super(RepeatedId, self).__init__(error_record=ER.REPEATED_STUDENT_ID, fields=fields)
