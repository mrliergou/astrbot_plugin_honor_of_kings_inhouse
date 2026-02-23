"""
管理员权限服务模块
"""
from ..repositories.state_repository import get_repository


class AuthService:
    """权限服务"""

    def __init__(self):
        self.repository = get_repository()

    async def is_admin(self, chat_id: str, user_id: str) -> bool:
        """
        检查用户是否是管理员

        Args:
            chat_id: 群组ID
            user_id: 用户ID

        Returns:
            是否是管理员
        """
        chat_state = await self.repository.get_chat_state(chat_id)
        return user_id in chat_state.config.admin_users

    async def add_admin(self, chat_id: str, user_id: str):
        """
        添加管理员

        Args:
            chat_id: 群组ID
            user_id: 用户ID
        """
        async with await self.repository.with_chat_lock(chat_id):
            chat_state = await self.repository.get_chat_state(chat_id)
            if user_id not in chat_state.config.admin_users:
                chat_state.config.admin_users.append(user_id)
                await self.repository.update_chat_state(chat_id, chat_state)

    async def remove_admin(self, chat_id: str, user_id: str):
        """
        移除管理员

        Args:
            chat_id: 群组ID
            user_id: 用户ID
        """
        async with await self.repository.with_chat_lock(chat_id):
            chat_state = await self.repository.get_chat_state(chat_id)
            if user_id in chat_state.config.admin_users:
                chat_state.config.admin_users.remove(user_id)
                await self.repository.update_chat_state(chat_id, chat_state)
