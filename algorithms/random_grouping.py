"""
随机分组算法模块
"""
import random
from typing import List, Tuple
from ..models import Player, TeamAssignment
from ..constants import Role, TeamSide, TEAM_SIZE


def random_group(players: List[Player]) -> Tuple[TeamAssignment, TeamAssignment]:
    """
    随机分组算法（Fisher-Yates 洗牌 + 阵营切分）

    Args:
        players: 玩家列表（必须是10人）

    Returns:
        (red_team, blue_team) 元组

    Raises:
        ValueError: 如果玩家数量不是10人
    """
    if len(players) != 10:
        raise ValueError(f"玩家数量必须是10人，当前为{len(players)}人")

    # Fisher-Yates 洗牌
    shuffled_players = players.copy()
    random.shuffle(shuffled_players)

    # 切分为两队
    red_players = shuffled_players[:TEAM_SIZE]
    blue_players = shuffled_players[TEAM_SIZE:]

    # 随机分配位置
    roles = list(Role)
    random.shuffle(roles)

    red_team = TeamAssignment(
        side=TeamSide.RED,
        role_to_user={roles[i]: red_players[i].user_id for i in range(TEAM_SIZE)},
        score=0
    )

    blue_team = TeamAssignment(
        side=TeamSide.BLUE,
        role_to_user={roles[i]: blue_players[i].user_id for i in range(TEAM_SIZE)},
        score=0
    )

    return red_team, blue_team
