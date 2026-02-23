"""
数据模型定义模块
"""
from dataclasses import dataclass, field
from typing import Optional
from .constants import Role, SignupMode, TeamSide, MatchStatus


@dataclass
class Player:
    """玩家实体"""
    user_id: str                    # 唯一标识
    nickname: str                   # 昵称
    chat_id: str                    # 群组ID
    signup_mode: SignupMode         # 报名模式
    preferred_roles: list[Role]     # 偏好分路（0或2个）
    signup_ts: int                  # 报名时间戳
    expires_at_ts: int              # 过期时间戳


@dataclass
class SignupPool:
    """报名池实体"""
    chat_id: str                    # 群组ID
    players: dict[str, Player]      # user_id -> Player
    queue_order: list[str]          # 报名顺序
    updated_ts: int                 # 更新时间戳

    def __post_init__(self):
        if self.players is None:
            self.players = {}
        if self.queue_order is None:
            self.queue_order = []


@dataclass
class TeamAssignment:
    """队伍分配实体"""
    side: TeamSide                  # 红方/蓝方
    role_to_user: dict[Role, str]   # 位置 -> user_id
    score: int = 0                  # 偏好命中分

    def __post_init__(self):
        if self.role_to_user is None:
            self.role_to_user = {}


@dataclass
class MatchRecord:
    """对局记录实体"""
    match_id: str                   # 对局ID
    chat_id: str                    # 群组ID
    created_ts: int                 # 创建时间戳
    algorithm: str                  # 算法类型（random/greedy/mcmf）
    red_team: TeamAssignment        # 红方阵容
    blue_team: TeamAssignment       # 蓝方阵容
    participants: list[str]         # 参与者列表
    winner: Optional[str] = None    # 胜者（RED/BLUE/DRAW）
    status: MatchStatus = MatchStatus.PENDING_ARCHIVE  # 状态
    preference_score_total: int = 0 # 总偏好分
    meta: dict[str, str] = field(default_factory=dict)  # 元数据


@dataclass
class ChatConfig:
    """群组配置实体"""
    ttl_hours: int = 5              # 报名数据过期时间（小时）
    max_history: int = 500          # 最大历史记录数
    admin_users: list[str] = field(default_factory=list)  # 管理员用户列表
    algorithm: str = "mcmf"         # 默认算法


@dataclass
class ChatState:
    """群组状态实体"""
    chat_id: str                    # 群组ID
    signup_pool: SignupPool         # 报名池
    history: list[MatchRecord]      # 历史记录
    pending_archive_match_id: Optional[str] = None  # 待归档对局ID
    config: ChatConfig = field(default_factory=ChatConfig)  # 配置
    last_midnight_reset_date: str = ""  # 最后午夜重置日期（YYYY-MM-DD）

    def __post_init__(self):
        if self.history is None:
            self.history = []


@dataclass
class GlobalState:
    """全局状态实体"""
    version: int                    # 版本号
    generated_at_ts: int            # 生成时间戳
    chats: dict[str, ChatState]     # chat_id -> ChatState

    def __post_init__(self):
        if self.chats is None:
            self.chats = {}
