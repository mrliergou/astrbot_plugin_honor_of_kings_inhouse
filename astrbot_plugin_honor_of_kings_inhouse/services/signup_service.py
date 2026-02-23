"""
报名服务模块
"""
from typing import Optional, Tuple
from dataclasses import dataclass
from ..models import Player, SignupPool
from ..constants import (
    Role, SignupMode, MAX_PLAYERS, ROLE_EMOJI, STATUS_ICONS,
    DEFAULT_TTL_HOURS
)
from ..repositories.state_repository import get_repository
from ..utils.time_utils import (
    get_current_timestamp, get_expiry_timestamp,
    is_expired, format_timestamp, get_time_until,
    is_new_day, get_current_date
)
from ..errors import (
    NotSignedUpError, ExcessPlayersError
)


@dataclass
class SignupResult:
    """报名结果"""
    success: bool
    message: str
    is_update: bool = False  # 是否是更新报名


@dataclass
class CancelResult:
    """取消报名结果"""
    success: bool
    message: str


@dataclass
class BoardView:
    """报名看板视图"""
    message: str


class SignupService:
    """报名服务"""

    def __init__(self):
        self.repository = get_repository()

    async def register(
        self,
        chat_id: str,
        user_id: str,
        nickname: str,
        role1: Optional[Role] = None,
        role2: Optional[Role] = None
    ) -> SignupResult:
        """
        报名

        Args:
            chat_id: 群组ID
            user_id: 用户ID
            nickname: 昵称
            role1: 首选分路（None 表示随机模式）
            role2: 次选分路

        Returns:
            SignupResult 实例
        """
        async with await self.repository.with_chat_lock(chat_id):
            # 获取群组状态
            chat_state = await self.repository.get_chat_state(chat_id)

            # 检查午夜重置
            await self._check_midnight_reset(chat_state)

            # 清理过期报名
            await self._cleanup_expired_internal(chat_state)

            pool = chat_state.signup_pool
            is_update = user_id in pool.players

            # 检查人数限制（如果是新报名）
            if not is_update and len(pool.players) >= MAX_PLAYERS:
                raise ExcessPlayersError()

            # 确定报名模式
            if role1 is None:
                signup_mode = SignupMode.RANDOM
                preferred_roles = []
            else:
                signup_mode = SignupMode.PREFERENCE
                preferred_roles = [role1] if role2 is None else [role1, role2]

            # 创建或更新玩家
            ttl_hours = chat_state.config.ttl_hours
            player = Player(
                user_id=user_id,
                nickname=nickname,
                chat_id=chat_id,
                signup_mode=signup_mode,
                preferred_roles=preferred_roles,
                signup_ts=get_current_timestamp(),
                expires_at_ts=get_expiry_timestamp(ttl_hours)
            )

            pool.players[user_id] = player

            # 更新队列顺序
            if not is_update:
                pool.queue_order.append(user_id)

            pool.updated_ts = get_current_timestamp()

            # 持久化
            await self.repository.update_chat_state(chat_id, chat_state)

            # 生成返回消息
            message = self._format_signup_message(player, len(pool.players), is_update)

            return SignupResult(
                success=True,
                message=message,
                is_update=is_update
            )

    async def cancel(self, chat_id: str, user_id: str) -> CancelResult:
        """
        取消报名

        Args:
            chat_id: 群组ID
            user_id: 用户ID

        Returns:
            CancelResult 实例
        """
        async with await self.repository.with_chat_lock(chat_id):
            # 获取群组状态
            chat_state = await self.repository.get_chat_state(chat_id)
            pool = chat_state.signup_pool

            # 检查是否已报名
            if user_id not in pool.players:
                raise NotSignedUpError()

            # 移除玩家
            player = pool.players[user_id]
            del pool.players[user_id]
            pool.queue_order.remove(user_id)
            pool.updated_ts = get_current_timestamp()

            # 持久化
            await self.repository.update_chat_state(chat_id, chat_state)

            message = f"{STATUS_ICONS['success']} 已取消报名：{player.nickname}"
            return CancelResult(success=True, message=message)

    async def list_board(self, chat_id: str) -> BoardView:
        """
        获取报名看板

        Args:
            chat_id: 群组ID

        Returns:
            BoardView 实例
        """
        # 获取群组状态
        chat_state = await self.repository.get_chat_state(chat_id)

        # 清理过期报名
        async with await self.repository.with_chat_lock(chat_id):
            await self._cleanup_expired_internal(chat_state)
            await self.repository.update_chat_state(chat_id, chat_state)

        pool = chat_state.signup_pool

        # 生成看板消息
        message = self._format_board_message(pool, chat_state.config.ttl_hours)

        return BoardView(message=message)

    async def cleanup_expired(self, chat_id: str) -> int:
        """
        清理过期报名

        Args:
            chat_id: 群组ID

        Returns:
            清理的玩家数量
        """
        async with await self.repository.with_chat_lock(chat_id):
            chat_state = await self.repository.get_chat_state(chat_id)
            count = await self._cleanup_expired_internal(chat_state)
            if count > 0:
                await self.repository.update_chat_state(chat_id, chat_state)
            return count

    async def _cleanup_expired_internal(self, chat_state) -> int:
        """
        内部清理过期报名方法

        Args:
            chat_state: 群组状态

        Returns:
            清理的玩家数量
        """
        pool = chat_state.signup_pool
        now = get_current_timestamp()

        expired_users = [
            uid for uid, player in pool.players.items()
            if is_expired(player.expires_at_ts)
        ]

        for uid in expired_users:
            del pool.players[uid]
            pool.queue_order.remove(uid)

        if expired_users:
            pool.updated_ts = now

        return len(expired_users)

    async def _check_midnight_reset(self, chat_state):
        """
        检查午夜重置

        Args:
            chat_state: 群组状态
        """
        if is_new_day(chat_state.last_midnight_reset_date):
            # 清空报名池
            chat_state.signup_pool.players.clear()
            chat_state.signup_pool.queue_order.clear()
            chat_state.signup_pool.updated_ts = get_current_timestamp()
            chat_state.last_midnight_reset_date = get_current_date()

    def _format_signup_message(
        self,
        player: Player,
        total_count: int,
        is_update: bool
    ) -> str:
        """
        格式化报名消息

        Args:
            player: 玩家实体
            total_count: 总报名人数
            is_update: 是否是更新

        Returns:
            格式化的消息
        """
        icon = STATUS_ICONS['success']
        action = "报名已更新" if is_update else "报名成功"

        lines = [
            f"{icon} {action}！",
            f"玩家：{player.nickname}"
        ]

        if player.signup_mode == SignupMode.PREFERENCE:
            if len(player.preferred_roles) >= 1:
                role1 = player.preferred_roles[0]
                lines.append(f"首选：{ROLE_EMOJI[role1]} {role1.value}")
            if len(player.preferred_roles) >= 2:
                role2 = player.preferred_roles[1]
                lines.append(f"次选：{ROLE_EMOJI[role2]} {role2.value}")
        else:
            lines.append("模式：随机分组")

        lines.append(f"当前报名：{total_count}/{MAX_PLAYERS}")

        return "\n".join(lines)

    def _format_board_message(self, pool: SignupPool, ttl_hours: int) -> str:
        """
        格式化看板消息

        Args:
            pool: 报名池
            ttl_hours: 过期时长

        Returns:
            格式化的消息
        """
        count = len(pool.players)

        if count == 0:
            return f"{STATUS_ICONS['info']} 当前无人报名\n{STATUS_ICONS['tip']} 输入 /报名 [分路1] [分路2] 开始报名"

        lines = [
            f"--- {STATUS_ICONS['flag']} 王者内战报名 ({count}/{MAX_PLAYERS}) ---"
        ]

        # 统计各位置人数
        role_stats = self._calculate_role_stats(pool)

        # 显示各位置统计
        for role in Role:
            emoji = ROLE_EMOJI[role]
            primary_count, secondary_count = role_stats[role]
            players_in_role = self._get_players_by_role(pool, role)

            if players_in_role:
                player_names = ", ".join([p.nickname for p in players_in_role])
                overflow_warning = ""
                if primary_count > 2:
                    overflow_warning = f" [{STATUS_ICONS['warning']}溢出]"
                lines.append(f"{emoji} {role.value}: {player_names}{overflow_warning}")
            else:
                lines.append(f"{emoji} {role.value}: [空缺]")

        lines.append("-" * 26)

        # 过期时间提示
        if pool.players:
            # 找到最早过期的时间
            earliest_expiry = min(p.expires_at_ts for p in pool.players.values())
            expiry_time = format_timestamp(earliest_expiry)
            time_until = get_time_until(earliest_expiry)
            lines.append(f"{STATUS_ICONS['timer']} 自动过期: {expiry_time} ({time_until})")

        # 提示信息
        if count < MAX_PLAYERS:
            need = MAX_PLAYERS - count
            empty_roles = [role.value for role in Role if not self._get_players_by_role(pool, role)]
            if empty_roles:
                lines.append(f"{STATUS_ICONS['tip']} 提示: 还差 {need} 人，空缺位置：{', '.join(empty_roles)}")
            else:
                lines.append(f"{STATUS_ICONS['tip']} 提示: 还差 {need} 人即可开始分组")
        else:
            lines.append(f"{STATUS_ICONS['success']} 人数已满，可以开始分组！")

        return "\n".join(lines)

    def _calculate_role_stats(self, pool: SignupPool) -> dict:
        """
        计算各位置统计

        Args:
            pool: 报名池

        Returns:
            {Role: (primary_count, secondary_count)}
        """
        stats = {role: (0, 0) for role in Role}

        for player in pool.players.values():
            if player.signup_mode == SignupMode.PREFERENCE:
                if len(player.preferred_roles) >= 1:
                    role1 = player.preferred_roles[0]
                    primary, secondary = stats[role1]
                    stats[role1] = (primary + 1, secondary)
                if len(player.preferred_roles) >= 2:
                    role2 = player.preferred_roles[1]
                    primary, secondary = stats[role2]
                    stats[role2] = (primary, secondary + 1)

        return stats

    def _get_players_by_role(self, pool: SignupPool, role: Role) -> list[Player]:
        """
        获取报名了指定位置的玩家

        Args:
            pool: 报名池
            role: 位置

        Returns:
            玩家列表
        """
        players = []
        for player in pool.players.values():
            if player.signup_mode == SignupMode.PREFERENCE:
                if role in player.preferred_roles:
                    players.append(player)
        return players
