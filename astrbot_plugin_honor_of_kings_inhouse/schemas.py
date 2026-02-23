"""
序列化/反序列化模块
"""
import json
from typing import Any
from .models import (
    Player, SignupPool, TeamAssignment, MatchRecord,
    ChatConfig, ChatState, GlobalState
)
from .constants import Role, SignupMode, TeamSide, MatchStatus


class StateEncoder(json.JSONEncoder):
    """状态编码器"""

    def default(self, obj):
        if isinstance(obj, (Role, SignupMode, TeamSide, MatchStatus)):
            return obj.value
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        return super().default(obj)


def serialize_state(state: GlobalState) -> str:
    """序列化全局状态为JSON字符串"""
    return json.dumps(state, cls=StateEncoder, ensure_ascii=False, indent=2)


def deserialize_state(data: str) -> GlobalState:
    """反序列化JSON字符串为全局状态"""
    obj = json.loads(data)
    return _dict_to_global_state(obj)


def _dict_to_global_state(obj: dict) -> GlobalState:
    """字典转全局状态"""
    chats = {}
    for chat_id, chat_data in obj.get('chats', {}).items():
        chats[chat_id] = _dict_to_chat_state(chat_data)

    return GlobalState(
        version=obj.get('version', 1),
        generated_at_ts=obj.get('generated_at_ts', 0),
        chats=chats
    )


def _dict_to_chat_state(obj: dict) -> ChatState:
    """字典转群组状态"""
    signup_pool = _dict_to_signup_pool(obj.get('signup_pool', {}))
    history = [_dict_to_match_record(m) for m in obj.get('history', [])]
    config = _dict_to_chat_config(obj.get('config', {}))

    return ChatState(
        chat_id=obj.get('chat_id', ''),
        signup_pool=signup_pool,
        history=history,
        pending_archive_match_id=obj.get('pending_archive_match_id'),
        config=config,
        last_midnight_reset_date=obj.get('last_midnight_reset_date', '')
    )


def _dict_to_signup_pool(obj: dict) -> SignupPool:
    """字典转报名池"""
    players = {}
    for user_id, player_data in obj.get('players', {}).items():
        players[user_id] = _dict_to_player(player_data)

    return SignupPool(
        chat_id=obj.get('chat_id', ''),
        players=players,
        queue_order=obj.get('queue_order', []),
        updated_ts=obj.get('updated_ts', 0)
    )


def _dict_to_player(obj: dict) -> Player:
    """字典转玩家"""
    preferred_roles = [Role(r) for r in obj.get('preferred_roles', [])]
    signup_mode = SignupMode(obj.get('signup_mode', SignupMode.RANDOM.value))

    return Player(
        user_id=obj.get('user_id', ''),
        nickname=obj.get('nickname', ''),
        chat_id=obj.get('chat_id', ''),
        signup_mode=signup_mode,
        preferred_roles=preferred_roles,
        signup_ts=obj.get('signup_ts', 0),
        expires_at_ts=obj.get('expires_at_ts', 0)
    )


def _dict_to_match_record(obj: dict) -> MatchRecord:
    """字典转对局记录"""
    red_team = _dict_to_team_assignment(obj.get('red_team', {}))
    blue_team = _dict_to_team_assignment(obj.get('blue_team', {}))
    status = MatchStatus(obj.get('status', MatchStatus.PENDING_ARCHIVE.value))

    return MatchRecord(
        match_id=obj.get('match_id', ''),
        chat_id=obj.get('chat_id', ''),
        created_ts=obj.get('created_ts', 0),
        algorithm=obj.get('algorithm', ''),
        red_team=red_team,
        blue_team=blue_team,
        participants=obj.get('participants', []),
        winner=obj.get('winner'),
        status=status,
        preference_score_total=obj.get('preference_score_total', 0),
        meta=obj.get('meta', {})
    )


def _dict_to_team_assignment(obj: dict) -> TeamAssignment:
    """字典转队伍分配"""
    side = TeamSide(obj.get('side', TeamSide.RED.value))
    role_to_user = {}
    for role_str, user_id in obj.get('role_to_user', {}).items():
        role_to_user[Role(role_str)] = user_id

    return TeamAssignment(
        side=side,
        role_to_user=role_to_user,
        score=obj.get('score', 0)
    )


def _dict_to_chat_config(obj: dict) -> ChatConfig:
    """字典转群组配置"""
    return ChatConfig(
        ttl_hours=obj.get('ttl_hours', 5),
        max_history=obj.get('max_history', 500),
        admin_users=obj.get('admin_users', []),
        algorithm=obj.get('algorithm', 'mcmf')
    )
