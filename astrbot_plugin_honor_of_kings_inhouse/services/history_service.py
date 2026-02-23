"""
历史统计服务模块
"""
from dataclasses import dataclass
from typing import List
from ..models import MatchRecord
from ..constants import STATUS_ICONS
from ..repositories.state_repository import get_repository


@dataclass
class HistoryResult:
    """历史查询结果"""
    message: str


class HistoryService:
    """历史服务"""

    def __init__(self):
        self.repository = get_repository()

    async def query_matches(self, chat_id: str, limit: int = 10) -> HistoryResult:
        """
        查询历史对局

        Args:
            chat_id: 群组ID
            limit: 查询数量

        Returns:
            HistoryResult 实例
        """
        chat_state = await self.repository.get_chat_state(chat_id)
        history = chat_state.history[-limit:] if len(chat_state.history) > limit else chat_state.history

        if not history:
            message = f"{STATUS_ICONS['info']} 暂无历史对局记录"
            return HistoryResult(message=message)

        lines = [f"--- {STATUS_ICONS['info']} 历史对局记录 ---"]

        for i, match in enumerate(reversed(history), 1):
            winner_text = match.winner if match.winner else "未归档"
            lines.append(f"{i}. {match.algorithm} | 胜者: {winner_text}")

        message = "\n".join(lines)
        return HistoryResult(message=message)

    async def win_rate(self, chat_id: str) -> HistoryResult:
        """
        胜率统计（简化版）

        Args:
            chat_id: 群组ID

        Returns:
            HistoryResult 实例
        """
        chat_state = await self.repository.get_chat_state(chat_id)
        archived_matches = [m for m in chat_state.history if m.winner]

        if not archived_matches:
            message = f"{STATUS_ICONS['info']} 暂无已归档的对局"
            return HistoryResult(message=message)

        red_wins = sum(1 for m in archived_matches if m.winner == "RED")
        blue_wins = sum(1 for m in archived_matches if m.winner == "BLUE")
        draws = sum(1 for m in archived_matches if m.winner == "DRAW")

        message = f"""--- {STATUS_ICONS['info']} 胜率统计 ---
总对局: {len(archived_matches)}
红方胜: {red_wins}
蓝方胜: {blue_wins}
平局: {draws}"""

        return HistoryResult(message=message)
