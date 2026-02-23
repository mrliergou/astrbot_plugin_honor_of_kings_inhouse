"""
时间工具模块
"""
import time
from datetime import datetime, timezone, timedelta


def get_current_timestamp() -> int:
    """获取当前时间戳（秒）"""
    return int(time.time())


def get_expiry_timestamp(ttl_hours: int) -> int:
    """
    获取过期时间戳

    Args:
        ttl_hours: 过期时长（小时）

    Returns:
        过期时间戳（秒）
    """
    return get_current_timestamp() + ttl_hours * 3600


def get_current_date() -> str:
    """
    获取当前日期字符串（YYYY-MM-DD）

    Returns:
        日期字符串
    """
    return datetime.now().strftime("%Y-%m-%d")


def format_timestamp(ts: int) -> str:
    """
    格式化时间戳为可读字符串

    Args:
        ts: 时间戳（秒）

    Returns:
        格式化的时间字符串（HH:MM）
    """
    dt = datetime.fromtimestamp(ts)
    return dt.strftime("%H:%M")


def get_time_until(target_ts: int) -> str:
    """
    获取距离目标时间的剩余时间描述

    Args:
        target_ts: 目标时间戳（秒）

    Returns:
        剩余时间描述（如 "4h后"）
    """
    now = get_current_timestamp()
    diff = target_ts - now

    if diff <= 0:
        return "已过期"

    hours = diff // 3600
    minutes = (diff % 3600) // 60

    if hours > 0:
        return f"{hours}h后"
    elif minutes > 0:
        return f"{minutes}min后"
    else:
        return "即将过期"


def is_expired(expires_at_ts: int) -> bool:
    """
    检查是否已过期

    Args:
        expires_at_ts: 过期时间戳（秒）

    Returns:
        是否已过期
    """
    return get_current_timestamp() >= expires_at_ts


def is_new_day(last_date: str) -> bool:
    """
    检查是否是新的一天

    Args:
        last_date: 上次日期字符串（YYYY-MM-DD）

    Returns:
        是否是新的一天
    """
    current_date = get_current_date()
    return current_date != last_date
