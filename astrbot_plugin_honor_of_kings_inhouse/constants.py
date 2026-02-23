"""
常量定义模块
包含枚举类型、Emoji映射、默认配置、错误码等
"""
from enum import Enum


class Role(Enum):
    """游戏位置枚举"""
    TOP = "上单"
    JUNGLE = "打野"
    MID = "中单"
    ADC = "射手"
    SUPPORT = "辅助"


class SignupMode(Enum):
    """报名模式枚举"""
    RANDOM = "random"           # 随机分组模式
    PREFERENCE = "preference"   # 智能分组模式


class TeamSide(Enum):
    """队伍方枚举"""
    RED = "红方"
    BLUE = "蓝方"


class MatchStatus(Enum):
    """对局状态枚举"""
    PENDING_ARCHIVE = "待归档"
    ARCHIVED = "已归档"
    DISCARDED = "已废弃"


# 分路缩写映射
ROLE_ALIASES = {
    "上单": Role.TOP, "上": Role.TOP, "边": Role.TOP, "战": Role.TOP,
    "打野": Role.JUNGLE, "野": Role.JUNGLE, "刺": Role.JUNGLE,
    "中单": Role.MID, "中": Role.MID, "法": Role.MID,
    "射手": Role.ADC, "射": Role.ADC, "后": Role.ADC,
    "辅助": Role.SUPPORT, "辅": Role.SUPPORT, "肉": Role.SUPPORT, "盾": Role.SUPPORT,
}

# Emoji 映射
ROLE_EMOJI = {
    Role.TOP: "🛡️",
    Role.JUNGLE: "⚔️",
    Role.MID: "🧙‍♂️",
    Role.ADC: "🏹",
    Role.SUPPORT: "🚀",
}

# 状态图标
STATUS_ICONS = {
    "success": "✅",
    "error": "❌",
    "warning": "⚠️",
    "info": "ℹ️",
    "forbidden": "🚫",
    "timer": "⏱️",
    "tip": "💡",
    "flag": "🚩",
    "balance": "⚖️",
}

# 队伍图标
TEAM_ICONS = {
    TeamSide.RED: "🔴",
    TeamSide.BLUE: "🔵",
}

# 默认配置
DEFAULT_TTL_HOURS = 5  # 报名数据过期时间（小时）
MAX_HISTORY_PER_CHAT = 500  # 每个群组最大历史记录数
MAX_PLAYERS = 10  # 最大报名人数
TEAM_SIZE = 5  # 每队人数

# 算法类型
ALGORITHM_RANDOM = "random"
ALGORITHM_GREEDY = "greedy"
ALGORITHM_MCMF = "mcmf"

# 错误码
class ErrorCode(Enum):
    """业务错误码"""
    ERR_INVALID_ROLE = "ERR_INVALID_ROLE"
    ERR_DUPLICATE_SIGNUP = "ERR_DUPLICATE_SIGNUP"
    ERR_NOT_SIGNED_UP = "ERR_NOT_SIGNED_UP"
    ERR_INSUFFICIENT_PLAYERS = "ERR_INSUFFICIENT_PLAYERS"
    ERR_EXCESS_PLAYERS = "ERR_EXCESS_PLAYERS"
    ERR_FORBIDDEN = "ERR_FORBIDDEN"
    ERR_STATE_CORRUPTED = "ERR_STATE_CORRUPTED"
    ERR_NO_VALID_ASSIGNMENT = "ERR_NO_VALID_ASSIGNMENT"
    ERR_NO_PENDING_MATCH = "ERR_NO_PENDING_MATCH"

# 错误消息映射
ERROR_MESSAGES = {
    ErrorCode.ERR_INVALID_ROLE: "❌ 无效的位置名称，请使用：上/野/中/射/辅",
    ErrorCode.ERR_DUPLICATE_SIGNUP: "✅ 报名已更新",
    ErrorCode.ERR_NOT_SIGNED_UP: "❌ 你还没有报名",
    ErrorCode.ERR_INSUFFICIENT_PLAYERS: "⚠️ 当前 {count} 人，还差 {need} 人才能开始分组",
    ErrorCode.ERR_EXCESS_PLAYERS: "⚠️ 报名已满，请等待下一局或联系管理员清空",
    ErrorCode.ERR_FORBIDDEN: "🚫 权限拒绝：该操作仅限群管理员",
    ErrorCode.ERR_STATE_CORRUPTED: "❌ 数据状态异常，请联系管理员",
    ErrorCode.ERR_NO_VALID_ASSIGNMENT: "🚫 无法完成分组：位置冲突无法解决，请调整报名或使用随机分组",
    ErrorCode.ERR_NO_PENDING_MATCH: "❌ 没有待归档的对局",
}
