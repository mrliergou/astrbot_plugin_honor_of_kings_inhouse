"""
锁管理工具模块
"""
import asyncio
from typing import Dict


class LockManager:
    """锁管理器"""

    def __init__(self):
        self._locks: Dict[str, asyncio.Lock] = {}
        self._global_lock = asyncio.Lock()

    async def get_chat_lock(self, chat_id: str) -> asyncio.Lock:
        """
        获取群组级锁

        Args:
            chat_id: 群组ID

        Returns:
            asyncio.Lock 实例
        """
        if chat_id not in self._locks:
            async with self._global_lock:
                # 双重检查，避免并发创建
                if chat_id not in self._locks:
                    self._locks[chat_id] = asyncio.Lock()

        return self._locks[chat_id]

    def clear_lock(self, chat_id: str):
        """
        清除群组锁（用于清理不再使用的锁）

        Args:
            chat_id: 群组ID
        """
        if chat_id in self._locks:
            del self._locks[chat_id]


# 全局锁管理器实例
_lock_manager = LockManager()


async def get_chat_lock(chat_id: str) -> asyncio.Lock:
    """
    获取群组级锁（便捷函数）

    Args:
        chat_id: 群组ID

    Returns:
        asyncio.Lock 实例
    """
    return await _lock_manager.get_chat_lock(chat_id)
