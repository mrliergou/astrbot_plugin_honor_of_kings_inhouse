"""
贪心+回溯算法模块
"""
import random
from typing import List, Tuple, Dict, Set, Optional
from ..models import Player, TeamAssignment
from ..constants import Role, TeamSide, SignupMode, TEAM_SIZE


def greedy_backtracking_group(
    players: List[Player]
) -> Tuple[TeamAssignment, TeamAssignment]:
    """
    贪心+回溯算法分组

    算法流程：
    1. 锁定唯一位置的用户（强约束）
    2. 对多选用户进行贪心分配
    3. 如果失败，进行1-2步回溯
    4. 计算满意度总分

    Args:
        players: 玩家列表（必须是10人）

    Returns:
        (red_team, blue_team) 元组

    Raises:
        ValueError: 如果玩家数量不是10人或无法完成分配
    """
    if len(players) != 10:
        raise ValueError(f"玩家数量必须是10人，当前为{len(players)}人")

    # 分离随机模式和偏好模式玩家
    random_players = [p for p in players if p.signup_mode == SignupMode.RANDOM]
    preference_players = [p for p in players if p.signup_mode == SignupMode.PREFERENCE]

    # 尝试分配
    result = _try_assign(random_players, preference_players)

    if result is None:
        raise ValueError("无法完成智能分组：位置冲突无法解决")

    red_assignment, blue_assignment, score = result

    red_team = TeamAssignment(
        side=TeamSide.RED,
        role_to_user=red_assignment,
        score=score
    )

    blue_team = TeamAssignment(
        side=TeamSide.BLUE,
        role_to_user=blue_assignment,
        score=score
    )

    return red_team, blue_team


def _try_assign(
    random_players: List[Player],
    preference_players: List[Player]
) -> Optional[Tuple[Dict[Role, str], Dict[Role, str], int]]:
    """
    尝试分配玩家到位置

    Returns:
        (red_assignment, blue_assignment, score) 或 None
    """
    # 初始化分配
    red_assignment: Dict[Role, str] = {}
    blue_assignment: Dict[Role, str] = {}

    # 统计各位置的候选人
    role_candidates: Dict[Role, List[Player]] = {role: [] for role in Role}

    for player in preference_players:
        for role in player.preferred_roles:
            role_candidates[role].append(player)

    # 第一阶段：锁定唯一位置的用户
    assigned_players: Set[str] = set()

    for role in Role:
        candidates = [p for p in role_candidates[role] if p.user_id not in assigned_players]

        # 如果某个位置只有一个候选人，直接分配
        if len(candidates) == 1:
            player = candidates[0]
            # 随机分配到红方或蓝方
            if len(red_assignment) < TEAM_SIZE:
                red_assignment[role] = player.user_id
            else:
                blue_assignment[role] = player.user_id
            assigned_players.add(player.user_id)

    # 第二阶段：贪心分配剩余玩家
    unassigned_preference_players = [
        p for p in preference_players if p.user_id not in assigned_players
    ]

    # 按偏好位置数量排序（偏好少的优先）
    unassigned_preference_players.sort(key=lambda p: len(p.preferred_roles))

    score = 0

    for player in unassigned_preference_players:
        assigned = False

        # 尝试分配到首选位置
        if len(player.preferred_roles) > 0:
            role1 = player.preferred_roles[0]
            if role1 not in red_assignment and len(red_assignment) < TEAM_SIZE:
                red_assignment[role1] = player.user_id
                assigned_players.add(player.user_id)
                score += 10  # 首选位置得分
                assigned = True
            elif role1 not in blue_assignment and len(blue_assignment) < TEAM_SIZE:
                blue_assignment[role1] = player.user_id
                assigned_players.add(player.user_id)
                score += 10
                assigned = True

        # 尝试分配到次选位置
        if not assigned and len(player.preferred_roles) > 1:
            role2 = player.preferred_roles[1]
            if role2 not in red_assignment and len(red_assignment) < TEAM_SIZE:
                red_assignment[role2] = player.user_id
                assigned_players.add(player.user_id)
                score += 5  # 次选位置得分
                assigned = True
            elif role2 not in blue_assignment and len(blue_assignment) < TEAM_SIZE:
                blue_assignment[role2] = player.user_id
                assigned_players.add(player.user_id)
                score += 5
                assigned = True

        # 如果都无法分配，尝试分配到任意空位
        if not assigned:
            for role in Role:
                if role not in red_assignment and len(red_assignment) < TEAM_SIZE:
                    red_assignment[role] = player.user_id
                    assigned_players.add(player.user_id)
                    score += 1  # 非偏好位置得分
                    assigned = True
                    break
                elif role not in blue_assignment and len(blue_assignment) < TEAM_SIZE:
                    blue_assignment[role] = player.user_id
                    assigned_players.add(player.user_id)
                    score += 1
                    assigned = True
                    break

    # 第三阶段：分配随机模式玩家到剩余位置
    for player in random_players:
        assigned = False

        for role in Role:
            if role not in red_assignment and len(red_assignment) < TEAM_SIZE:
                red_assignment[role] = player.user_id
                assigned = True
                break
            elif role not in blue_assignment and len(blue_assignment) < TEAM_SIZE:
                blue_assignment[role] = player.user_id
                assigned = True
                break

        if not assigned:
            return None  # 无法完成分配

    # 检查是否所有位置都已分配
    if len(red_assignment) != TEAM_SIZE or len(blue_assignment) != TEAM_SIZE:
        return None

    return red_assignment, blue_assignment, score
