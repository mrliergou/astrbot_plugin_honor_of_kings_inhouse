"""
王者荣耀内战报名分组插件
"""
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

from .command_parser import parse_roles
from .services.signup_service import SignupService
from .services.grouping_service import GroupingService
from .services.history_service import HistoryService
from .services.auth_service import AuthService
from .errors import (
    BusinessError, InvalidRoleError, NotSignedUpError,
    InsufficientPlayersError, ExcessPlayersError,
    ForbiddenError, NoValidAssignmentError, NoPendingMatchError
)
from .constants import STATUS_ICONS


@register(
    "honor_of_kings_inhouse",
    "Claude",
    "王者荣耀内战报名和智能分组系统",
    "1.0.0",
    "https://github.com/yourusername/astrbot_plugin_honor_of_kings_inhouse"
)
class HonorOfKingsInhousePlugin(Star):
    """王者荣耀内战插件"""

    def __init__(self, context: Context):
        super().__init__(context)
        self.signup_service = SignupService()
        self.grouping_service = GroupingService()
        self.history_service = HistoryService()
        self.auth_service = AuthService()
        logger.info("王者荣耀内战插件已加载")

    @filter.command("报名")
    async def cmd_signup(self, event: AstrMessageEvent):
        """报名命令"""
        try:
            chat_id = self._get_chat_id(event)
            user_id = event.get_sender_id()
            nickname = event.get_sender_name()

            # 解析参数
            message_str = event.message_str.strip()
            args = message_str.split()[1:] if len(message_str.split()) > 1 else []

            # 解析分路
            role1, role2 = parse_roles(args)

            # 执行报名
            result = await self.signup_service.register(
                chat_id, user_id, nickname, role1, role2
            )

            yield event.plain_result(result.message)

        except BusinessError as e:
            yield event.plain_result(e.message)
        except Exception as e:
            logger.error(f"报名命令执行失败: {e}")
            yield event.plain_result(f"{STATUS_ICONS['error']} 命令执行失败，请稍后重试")

    @filter.command("取消报名")
    async def cmd_cancel(self, event: AstrMessageEvent):
        """取消报名命令"""
        try:
            chat_id = self._get_chat_id(event)
            user_id = event.get_sender_id()

            result = await self.signup_service.cancel(chat_id, user_id)
            yield event.plain_result(result.message)

        except BusinessError as e:
            yield event.plain_result(e.message)
        except Exception as e:
            logger.error(f"取消报名命令执行失败: {e}")
            yield event.plain_result(f"{STATUS_ICONS['error']} 命令执行失败，请稍后重试")

    @filter.command("报名列表")
    async def cmd_list(self, event: AstrMessageEvent):
        """报名列表命令"""
        try:
            chat_id = self._get_chat_id(event)

            result = await self.signup_service.list_board(chat_id)
            yield event.plain_result(result.message)

        except Exception as e:
            logger.error(f"报名列表命令执行失败: {e}")
            yield event.plain_result(f"{STATUS_ICONS['error']} 命令执行失败，请稍后重试")

    @filter.command("随机分组")
    async def cmd_random_group(self, event: AstrMessageEvent):
        """随机分组命令"""
        try:
            chat_id = self._get_chat_id(event)
            user_id = event.get_sender_id()

            result = await self.grouping_service.random_group(chat_id, user_id)
            yield event.plain_result(result.message)

        except BusinessError as e:
            yield event.plain_result(e.message)
        except Exception as e:
            logger.error(f"随机分组命令执行失败: {e}")
            yield event.plain_result(f"{STATUS_ICONS['error']} 命令执行失败，请稍后重试")

    @filter.command("智能分组")
    async def cmd_smart_group(self, event: AstrMessageEvent):
        """智能分组命令"""
        try:
            chat_id = self._get_chat_id(event)
            user_id = event.get_sender_id()

            result = await self.grouping_service.smart_group(chat_id, user_id)
            yield event.plain_result(result.message)

        except BusinessError as e:
            yield event.plain_result(e.message)
        except Exception as e:
            logger.error(f"智能分组命令执行失败: {e}")
            yield event.plain_result(f"{STATUS_ICONS['error']} 命令执行失败，请稍后重试")

    @filter.command("清空报名")
    async def cmd_clear(self, event: AstrMessageEvent):
        """清空报名命令（管理员）"""
        try:
            chat_id = self._get_chat_id(event)
            user_id = event.get_sender_id()

            # 检查权限
            is_admin = await self.auth_service.is_admin(chat_id, user_id)
            if not is_admin:
                raise ForbiddenError()

            # 清空报名池
            chat_state = await self.signup_service.repository.get_chat_state(chat_id)
            async with await self.signup_service.repository.with_chat_lock(chat_id):
                chat_state.signup_pool.players.clear()
                chat_state.signup_pool.queue_order.clear()
                await self.signup_service.repository.update_chat_state(chat_id, chat_state)

            yield event.plain_result(f"{STATUS_ICONS['success']} 报名池已清空")

        except BusinessError as e:
            yield event.plain_result(e.message)
        except Exception as e:
            logger.error(f"清空报名命令执行失败: {e}")
            yield event.plain_result(f"{STATUS_ICONS['error']} 命令执行失败，请稍后重试")

    @filter.command("历史对局")
    async def cmd_history(self, event: AstrMessageEvent):
        """历史对局命令"""
        try:
            chat_id = self._get_chat_id(event)

            result = await self.history_service.query_matches(chat_id)
            yield event.plain_result(result.message)

        except Exception as e:
            logger.error(f"历史对局命令执行失败: {e}")
            yield event.plain_result(f"{STATUS_ICONS['error']} 命令执行失败，请稍后重试")

    @filter.command("胜率统计")
    async def cmd_winrate(self, event: AstrMessageEvent):
        """胜率统计命令"""
        try:
            chat_id = self._get_chat_id(event)

            result = await self.history_service.win_rate(chat_id)
            yield event.plain_result(result.message)

        except Exception as e:
            logger.error(f"胜率统计命令执行失败: {e}")
            yield event.plain_result(f"{STATUS_ICONS['error']} 命令执行失败，请稍后重试")

    @filter.command("归档对局")
    async def cmd_archive(self, event: AstrMessageEvent):
        """归档对局命令"""
        try:
            chat_id = self._get_chat_id(event)

            # 解析参数
            message_str = event.message_str.strip()
            args = message_str.split()[1:] if len(message_str.split()) > 1 else []

            if not args:
                yield event.plain_result(f"{STATUS_ICONS['info']} 用法: /归档对局 [红|蓝|平]")
                return

            winner_map = {
                "红": "RED", "红方": "RED",
                "蓝": "BLUE", "蓝方": "BLUE",
                "平": "DRAW", "平局": "DRAW"
            }

            winner = winner_map.get(args[0])
            if not winner:
                yield event.plain_result(f"{STATUS_ICONS['error']} 无效的胜者，请使用：红/蓝/平")
                return

            result = await self.grouping_service.archive_match(chat_id, winner)
            yield event.plain_result(result.message)

        except BusinessError as e:
            yield event.plain_result(e.message)
        except Exception as e:
            logger.error(f"归档对局命令执行失败: {e}")
            yield event.plain_result(f"{STATUS_ICONS['error']} 命令执行失败，请稍后重试")

    def _get_chat_id(self, event: AstrMessageEvent) -> str:
        """
        获取群组ID

        Args:
            event: 消息事件

        Returns:
            群组ID
        """
        # 尝试获取群组ID，如果是私聊则使用用户ID
        if hasattr(event, 'group_id') and event.group_id:
            return str(event.group_id)
        return str(event.get_sender_id())

    async def terminate(self):
        """插件卸载时调用"""
        logger.info("王者荣耀内战插件已卸载")
