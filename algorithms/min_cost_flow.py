"""
最小费用最大流算法模块（简化版）

注意：这是一个基于贪心优化的简化实现，
真正的MCMF算法实现较为复杂，可作为后续优化项。
"""
import random
from typing import List, Tuple, Dict
from ..models import Player, TeamAssignment
from ..constants import Role, TeamSide, SignupMode, TEAM_SIZE


def min_cost_flow_group(
    players: List[Player]
) -> Tuple[TeamAssignment, TeamAssignment]:
    """
    最小费用最大流分组算法（简化版）

    使用贪心策略 + 多次随机采样 + 评分选优的方式
    模拟MCMF的效果

    Args:
        players: 玩家列表（必须是10人）

    Returns:
        (red_team, blue_team) 元组

    Raises:
        ValueError: 如果玩家数量不是10人或无法完成分配
    """
    if len(players) != 10:
        raise ValueError(f"玩家数量必须是10人，当前为{len(players)}人")

    # 多次采样，选择最优方案
    best_result = None
    best_score = -1

    # 尝试多次（Monte Carlo采样）
    for _ in range(20):
        result = _try_assign_with_cost(players)
        if result is not None:
            red_assignment, blue_assignment, score = result
            if score > best_score:
                best_score = score
                best_result = result

    if best_result is None:
        raise ValueError("无法完成智能分组：位置冲突无法解决")

    red_assignment, blue_assignment, score = best_result

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


def _try_assign_with_cost(
    players: List[Player]
) -> Tuple[Dict[Role, str], Dict[Role, str], int]:
    """
    尝试分配玩家到位置（带费用优化）

    费用函数：
    - 命中第一偏好：10分
    - 命中第二偏好：5分
    - 随机报名玩家：3分
    - 非偏好分配：1分

    Returns:
        (red_assignment, blue_assignment, score) 或 None
    """
    # 分离玩家
    random_players = [p for p in players if p.signup_mode == SignupMode.RANDOM]
    preference_players = [p for p in players if p.signup_mode == SignupMode.PREFERENCE]

    # 打乱顺序，增加随机性
    preference_players = preference_players.copy()
    random.shuffle(preference_players)

    # 初始化
    red_assignment: Dict[Role, str] = {}
    blue_assignment: Dict[Role, str] = {}
    assigned_players = set()
    total_score = 0

    # 构建候选矩阵
    player_role_scores: Dict[str, Dict[Role, int]] = {}

    for player in preference_players:
        player_role_scores[player.user_id] = {}
        if len(player.preferred_roles) > 0:
            player_role_scores[player.user_id][player.preferred_roles[0]] = 10
        if len(player.preferred_roles) > 1:
            player_role_scores[player.user_id][player.preferred_roles[1]] = 5
        # 其他位置得分为1
        for role in Role:
            if role not in player_role_scores[player.user_id]:
                player_role_scores[player.user_id][role] = 1

    # 贪心分配：每次选择得分最高的（玩家，位置，队伍）组合
    while len(assigned_players) < len(preference_players):
        best_assignment = None
        best_assignment_score = -1

        for player in preference_players:
            if player.user_id in assigned_players:
                continue

            for role in Role:
                # 尝试分配到红方
                if role not in red_assignment and len(red_assignment) < TEAM_SIZE:
                    score = player_role_scores[player.user_id].get(role, 1)
                    # 添加随机扰动
                    score += random.uniform(0, 0.5)

                    if score > best_assignment_score:
                        best_assignment_score = score
                        best_assignment = (player, role, 'red', score)

                # 尝试分配到蓝方
                if role not in blue_assignment and len(blue_assignment) < TEAM_SIZE:
                    score = player_role_scores[player.user_id].get(role, 1)
                    score += random.uniform(0, 0.5)

                    if score > best_assignment_score:
                        best_assignment_score = score
                        best_assignment = (player, role, 'blue', score)

        if best_assignment is None:
            return None  # 无法完成分配

        player, role, team, score = best_assignment
        if team == 'red':
            red_assignment[role] = player.user_id
        else:
            blue_assignment[role] = player.user_id

        assigned_players.add(player.user_id)
        total_score += int(score)

    # 分配随机模式玩家
    for player in random_players:
        assigned = False

        for role in Role:
            if role not in red_assignment and len(red_assignment) < TEAM_SIZE:
                red_assignment[role] = player.user_id
                total_score += 3
                assigned = True
                break
            elif role not in blue_assignment and len(blue_assignment) < TEAM_SIZE:
                blue_assignment[role] = player.user_id
                total_score += 3
                assigned = True
                break

        if not assigned:
            return None

    # 检查完整性
    if len(red_assignment) != TEAM_SIZE or len(blue_assignment) != TEAM_SIZE:
        return None

    return red_assignment, blue_assignment, total_score
