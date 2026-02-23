"""
命令参数解析模块
"""
from typing import Optional, Tuple
from .constants import Role, ROLE_ALIASES
from .errors import InvalidRoleError


def parse_roles(args: list[str]) -> Tuple[Optional[Role], Optional[Role]]:
    """
    解析分路参数

    Args:
        args: 命令参数列表

    Returns:
        (role1, role2) 元组，如果没有参数则返回 (None, None)

    Raises:
        InvalidRoleError: 如果分路名称无效
    """
    if not args:
        return None, None

    if len(args) == 1:
        # 只有一个参数，作为首选分路
        role1 = _parse_single_role(args[0])
        return role1, None

    # 两个参数
    role1 = _parse_single_role(args[0])
    role2 = _parse_single_role(args[1])

    # 检查是否重复
    if role1 == role2:
        raise InvalidRoleError()

    return role1, role2


def _parse_single_role(role_str: str) -> Role:
    """
    解析单个分路字符串

    Args:
        role_str: 分路字符串

    Returns:
        Role 枚举值

    Raises:
        InvalidRoleError: 如果分路名称无效
    """
    role_str = role_str.strip()

    # 查找别名映射
    if role_str in ROLE_ALIASES:
        return ROLE_ALIASES[role_str]

    # 尝试直接匹配枚举值
    for role in Role:
        if role.value == role_str:
            return role

    raise InvalidRoleError()


def format_role(role: Role) -> str:
    """
    格式化分路名称

    Args:
        role: Role 枚举值

    Returns:
        分路的中文名称
    """
    return role.value


def validate_command_args(command: str, args: list[str],
                         min_args: int = 0, max_args: int = None) -> bool:
    """
    验证命令参数数量

    Args:
        command: 命令名称
        args: 参数列表
        min_args: 最小参数数量
        max_args: 最大参数数量（None 表示不限制）

    Returns:
        是否有效
    """
    arg_count = len(args)

    if arg_count < min_args:
        return False

    if max_args is not None and arg_count > max_args:
        return False

    return True
