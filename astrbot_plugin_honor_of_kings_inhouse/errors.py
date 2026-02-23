"""
业务异常定义模块
"""
from .constants import ErrorCode, ERROR_MESSAGES


class BusinessError(Exception):
    """业务异常基类"""

    def __init__(self, code: ErrorCode, **kwargs):
        self.code = code
        self.kwargs = kwargs
        message = ERROR_MESSAGES.get(code, str(code))
        if kwargs:
            message = message.format(**kwargs)
        super().__init__(message)
        self.message = message


class InvalidRoleError(BusinessError):
    """无效的位置错误"""
    def __init__(self):
        super().__init__(ErrorCode.ERR_INVALID_ROLE)


class NotSignedUpError(BusinessError):
    """未报名错误"""
    def __init__(self):
        super().__init__(ErrorCode.ERR_NOT_SIGNED_UP)


class InsufficientPlayersError(BusinessError):
    """人数不足错误"""
    def __init__(self, count: int, need: int):
        super().__init__(ErrorCode.ERR_INSUFFICIENT_PLAYERS, count=count, need=need)


class ExcessPlayersError(BusinessError):
    """人数超额错误"""
    def __init__(self):
        super().__init__(ErrorCode.ERR_EXCESS_PLAYERS)


class ForbiddenError(BusinessError):
    """权限不足错误"""
    def __init__(self):
        super().__init__(ErrorCode.ERR_FORBIDDEN)


class StateCorruptedError(BusinessError):
    """状态损坏错误"""
    def __init__(self):
        super().__init__(ErrorCode.ERR_STATE_CORRUPTED)


class NoValidAssignmentError(BusinessError):
    """无有效分配错误"""
    def __init__(self):
        super().__init__(ErrorCode.ERR_NO_VALID_ASSIGNMENT)


class NoPendingMatchError(BusinessError):
    """无待归档对局错误"""
    def __init__(self):
        super().__init__(ErrorCode.ERR_NO_PENDING_MATCH)
