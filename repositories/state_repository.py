"""
状态仓库模块
负责数据持久化、加载和并发控制
"""
import os
import shutil
import asyncio
from pathlib import Path
from typing import Optional
from ..models import GlobalState, ChatState, SignupPool, ChatConfig
from ..schemas import serialize_state, deserialize_state
from ..utils.lock_utils import get_chat_lock
from ..utils.time_utils import get_current_timestamp
from ..errors import StateCorruptedError


class StateRepository:
    """状态仓库"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_file = self.data_dir / "hok_inhouse_state.json"
        self.tmp_file = self.data_dir / "hok_inhouse_state.json.tmp"
        self.bak_file = self.data_dir / "hok_inhouse_state.json.bak"
        self._state: Optional[GlobalState] = None
        self._state_lock = asyncio.Lock()

        # 确保数据目录存在
        self.data_dir.mkdir(parents=True, exist_ok=True)

    async def load(self) -> GlobalState:
        """
        加载全局状态

        Returns:
            GlobalState 实例

        Raises:
            StateCorruptedError: 如果状态文件损坏且无法恢复
        """
        async with self._state_lock:
            if self._state is not None:
                return self._state

            # 尝试加载主文件
            if self.data_file.exists():
                try:
                    with open(self.data_file, 'r', encoding='utf-8') as f:
                        data = f.read()
                    self._state = deserialize_state(data)
                    return self._state
                except Exception as e:
                    print(f"警告：主文件加载失败: {e}")

            # 尝试加载备份文件
            if self.bak_file.exists():
                try:
                    with open(self.bak_file, 'r', encoding='utf-8') as f:
                        data = f.read()
                    self._state = deserialize_state(data)
                    print("已从备份文件恢复状态")
                    # 立即保存到主文件
                    await self._save_internal(self._state)
                    return self._state
                except Exception as e:
                    print(f"警告：备份文件加载失败: {e}")

            # 初始化空状态
            self._state = GlobalState(
                version=1,
                generated_at_ts=get_current_timestamp(),
                chats={}
            )
            # 保存初始状态
            await self._save_internal(self._state)
            return self._state

    async def save(self, state: GlobalState):
        """
        保存全局状态（原子写入）

        Args:
            state: 要保存的全局状态
        """
        async with self._state_lock:
            await self._save_internal(state)
            self._state = state

    async def _save_internal(self, state: GlobalState):
        """
        内部保存方法（原子写入）

        Args:
            state: 要保存的全局状态
        """
        # 更新时间戳
        state.generated_at_ts = get_current_timestamp()

        # 序列化
        data = serialize_state(state)

        # 1. 写入临时文件
        with open(self.tmp_file, 'w', encoding='utf-8') as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())

        # 2. 备份旧文件
        if self.data_file.exists():
            shutil.copy2(self.data_file, self.bak_file)

        # 3. 原子替换
        os.replace(self.tmp_file, self.data_file)

    async def get_chat_state(self, chat_id: str) -> ChatState:
        """
        获取群组状态（如果不存在则创建）

        Args:
            chat_id: 群组ID

        Returns:
            ChatState 实例
        """
        state = await self.load()

        if chat_id not in state.chats:
            # 创建新的群组状态
            chat_state = ChatState(
                chat_id=chat_id,
                signup_pool=SignupPool(
                    chat_id=chat_id,
                    players={},
                    queue_order=[],
                    updated_ts=get_current_timestamp()
                ),
                history=[],
                config=ChatConfig()
            )
            state.chats[chat_id] = chat_state

        return state.chats[chat_id]

    async def update_chat_state(self, chat_id: str, chat_state: ChatState):
        """
        更新群组状态并持久化

        Args:
            chat_id: 群组ID
            chat_state: 群组状态
        """
        state = await self.load()
        state.chats[chat_id] = chat_state
        await self.save(state)

    async def with_chat_lock(self, chat_id: str):
        """
        获取群组级锁的上下文管理器

        Args:
            chat_id: 群组ID

        Returns:
            asyncio.Lock 实例
        """
        return await get_chat_lock(chat_id)

    async def snapshot(self, chat_id: str) -> ChatState:
        """
        获取群组状态的快照（只读）

        Args:
            chat_id: 群组ID

        Returns:
            ChatState 实例
        """
        return await self.get_chat_state(chat_id)


# 全局仓库实例
_repository: Optional[StateRepository] = None


def get_repository(data_dir: str = "data") -> StateRepository:
    """
    获取全局仓库实例

    Args:
        data_dir: 数据目录路径

    Returns:
        StateRepository 实例
    """
    global _repository
    if _repository is None:
        _repository = StateRepository(data_dir)
    return _repository
