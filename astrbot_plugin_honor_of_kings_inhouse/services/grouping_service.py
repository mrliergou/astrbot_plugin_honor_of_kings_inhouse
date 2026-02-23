"""
分组服务模块
"""
import uuid
from dataclasses import dataclass
from typing import Optional
from ..models import MatchRecord, TeamAssignment, SignupPool
from ..constants import (
    Role, TeamSide, MatchStatus, MAX_PLAYERS, TEAM_SIZE,
    ROLE_EMOJI, TEAM_ICONS, STATUS_ICONS, ALGORITHM_RANDOM,
    ALGORITHM_GREEDY, ALGORITHM_MCMF
)
from ..repositories.state_repository import get_repository
from ..utils.time_utils import get_current_timestamp
from ..errors import InsufficientPlayersError, NoPendingMatchError, NoValidAssignmentError
from ..algorithms.random_grouping import random_group
from ..algorithms.greedy_backtracking import greedy_backtracking_group
from ..algorithms.min_cost_flow import min_cost_flow_group


@dataclass
class GroupingResult:
    """分组结果"""
    success: bool
    message: str
    match_id: Optional[str] = None


@dataclass
class ArchiveResult:
    """归档结果"""
    success: bool
    message: str


class GroupingService:
    """分组服务"""

    def __init__(self):
        self.repository = get_repository()

    async def random_group(self, chat_id: str, operator_id: str) -> GroupingResult:
        """
        随机分组

        Args:
            chat_id: 群组ID
            operator_id: 操作者ID

        Returns:
            GroupingResult 实例
        """
        async with await self.repository.with_chat_lock(chat_id):
            # 获取群组状态
            chat_state = await self.repository.get_chat_state(chat_id)
            pool = chat_state.signup_pool

            # 检查人数
            if len(pool.players) < MAX_PLAYERS:
                raise InsufficientPlayersError(
                    count=len(pool.players),
                    need=MAX_PLAYERS - len(pool.players)
                )

            # 获取玩家列表（按报名顺序）
            players = [pool.players[uid] for uid in pool.queue_order[:MAX_PLAYERS]]

            # 执行随机分组
            red_team, blue_team = random_group(players)

            # 创建对局记录
            match_id = str(uuid.uuid4())
            match_record = MatchRecord(
                match_id=match_id,
                chat_id=chat_id,
                created_ts=get_current_timestamp(),
                algorithm=ALGORITHM_RANDOM,
                red_team=red_team,
                blue_team=blue_team,
                participants=[p.user_id for p in players],
                status=MatchStatus.PENDING_ARCHIVE
            )

            # 添加到历史记录
            chat_state.history.append(match_record)
            chat_state.pending_archive_match_id = match_id

            # 清空报名池
            pool.players.clear()
            pool.queue_order.clear()
            pool.updated_ts = get_current_timestamp()

            # 持久化
            await self.repository.update_chat_state(chat_id, chat_state)

            # 生成返回消息
            message = self._format_grouping_message(match_record, pool)

            return GroupingResult(
                success=True,
                message=message,
                match_id=match_id
            )

    async def smart_group(
        self,
        chat_id: str,
        operator_id: str,
        algorithm: str = "mcmf"
    ) -> GroupingResult:
        """
        智能分组

        Args:
            chat_id: 群组ID
            operator_id: 操作者ID
            algorithm: 算法类型（greedy/mcmf）

        Returns:
            GroupingResult 实例
        """
        async with await self.repository.with_chat_lock(chat_id):
            # 获取群组状态
            chat_state = await self.repository.get_chat_state(chat_id)
            pool = chat_state.signup_pool

            # 检查人数
            if len(pool.players) < MAX_PLAYERS:
                raise InsufficientPlayersError(
                    count=len(pool.players),
                    need=MAX_PLAYERS - len(pool.players)
                )

            # 获取玩家列表（按报名顺序）
            players = [pool.players[uid] for uid in pool.queue_order[:MAX_PLAYERS]]

            # 根据配置选择算法
            if algorithm == "greedy" or algorithm == ALGORITHM_GREEDY:
                try:
                    red_team, blue_team = greedy_backtracking_group(players)
                    algo_name = ALGORITHM_GREEDY
                except ValueError as e:
                    raise NoValidAssignmentError()
            else:  # mcmf
                try:
                    red_team, blue_team = min_cost_flow_group(players)
                    algo_name = ALGORITHM_MCMF
                except ValueError as e:
                    raise NoValidAssignmentError()

            # 创建对局记录
            match_id = str(uuid.uuid4())
            match_record = MatchRecord(
                match_id=match_id,
                chat_id=chat_id,
                created_ts=get_current_timestamp(),
                algorithm=algo_name,
                red_team=red_team,
                blue_team=blue_team,
                participants=[p.user_id for p in players],
                status=MatchStatus.PENDING_ARCHIVE,
                preference_score_total=red_team.score + blue_team.score
            )

            # 添加到历史记录
            chat_state.history.append(match_record)
            chat_state.pending_archive_match_id = match_id

            # 清空报名池
            pool.players.clear()
            pool.queue_order.clear()
            pool.updated_ts = get_current_timestamp()

            # 持久化
            await self.repository.update_chat_state(chat_id, chat_state)

            # 生成返回消息
            message = self._format_grouping_message(match_record, pool)

            return GroupingResult(
                success=True,
                message=message,
                match_id=match_id
            )

    async def archive_match(
        self,
        chat_id: str,
        winner: str
    ) -> ArchiveResult:
        """
        归档对局

        Args:
            chat_id: 群组ID
            winner: 胜者（RED/BLUE/DRAW）

        Returns:
            ArchiveResult 实例
        """
        async with await self.repository.with_chat_lock(chat_id):
            # 获取群组状态
            chat_state = await self.repository.get_chat_state(chat_id)

            # 检查是否有待归档对局
            if not chat_state.pending_archive_match_id:
                raise NoPendingMatchError()

            # 查找对局记录
            match_record = None
            for record in chat_state.history:
                if record.match_id == chat_state.pending_archive_match_id:
                    match_record = record
                    break

            if not match_record:
                raise NoPendingMatchError()

            # 更新对局结果
            match_record.winner = winner
            match_record.status = MatchStatus.ARCHIVED

            # 清除待归档标记
            chat_state.pending_archive_match_id = None

            # 持久化
            await self.repository.update_chat_state(chat_id, chat_state)

            message = f"{STATUS_ICONS['success']} 对局已归档，胜者：{winner}"
            return ArchiveResult(success=True, message=message)

    def _format_grouping_message(
        self,
        match_record: MatchRecord,
        pool: SignupPool
    ) -> str:
        """
        格式化分组消息

        Args:
            match_record: 对局记录
            pool: 报名池

        Returns:
            格式化的消息
        """
        lines = [
            f"--- {STATUS_ICONS['flag']} 对局分配结果 ---",
            ""
        ]

        # 蓝方阵容
        lines.append(f"{TEAM_ICONS[TeamSide.BLUE]} 蓝方 (Blue Team)")
        blue_line_parts = []
        for role in Role:
            user_id = match_record.blue_team.role_to_user.get(role)
            if user_id:
                # 从参与者中查找昵称
                nickname = self._get_nickname_from_participants(
                    user_id, match_record, pool
                )
                blue_line_parts.append(f"{ROLE_EMOJI[role]} {nickname}")
        lines.append(" | ".join(blue_line_parts))
        lines.append("")

        # 红方阵容
        lines.append(f"{TEAM_ICONS[TeamSide.RED]} 红方 (Red Team)")
        red_line_parts = []
        for role in Role:
            user_id = match_record.red_team.role_to_user.get(role)
            if user_id:
                nickname = self._get_nickname_from_participants(
                    user_id, match_record, pool
                )
                red_line_parts.append(f"{ROLE_EMOJI[role]} {nickname}")
        lines.append(" | ".join(red_line_parts))

        lines.append("-" * 26)

        # 算法信息
        if match_record.algorithm == ALGORITHM_RANDOM:
            lines.append(f"{STATUS_ICONS['info']} 分配方式: 随机分组")
        else:
            lines.append(f"{STATUS_ICONS['balance']} 分配方式: 智能分组")

        lines.append("祝各位召唤师大杀四方！")
        lines.append("")
        lines.append(f"{STATUS_ICONS['tip']} 对局结束后使用 /归档对局 [红|蓝|平] 记录结果")

        return "\n".join(lines)

    def _get_nickname_from_participants(
        self,
        user_id: str,
        match_record: MatchRecord,
        pool: SignupPool
    ) -> str:
        """
        从参与者中获取昵称

        Args:
            user_id: 用户ID
            match_record: 对局记录
            pool: 报名池

        Returns:
            昵称
        """
        # 尝试从报名池中获取（可能已清空）
        if user_id in pool.players:
            return pool.players[user_id].nickname

        # 返回用户ID的简短形式
        return user_id[:8] if len(user_id) > 8 else user_id
