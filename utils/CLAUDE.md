[根目录](../CLAUDE.md) > **utils**

# 工具层模块

> 通用工具函数，提供时间处理和锁管理功能

## 变更记录 (Changelog)

### 2026-02-23 20:34:56
- 初始化工具层文档

---

## 模块职责

工具层提供可复用的基础功能：
- 时间戳处理与格式化
- 过期检查与日期判断
- 异步锁的管理与分配

## 入口与启动

工具模块被服务层和仓储层导入使用：

```python
from ..utils.time_utils import get_current_timestamp, is_expired
from ..utils.lock_utils import get_chat_lock
```

## 对外接口

### time_utils (时间工具)

#### 核心函数
- `get_current_timestamp()` - 获取当前时间戳（秒）
- `get_expiry_timestamp(ttl_hours)` - 计算过期时间戳
- `get_current_date()` - 获取当前日期字符串（YYYY-MM-DD）
- `format_timestamp(ts)` - 格式化时间戳为 HH:MM
- `get_time_until(target_ts)` - 计算剩余时间描述（如 "4h后"）
- `is_expired(expires_at_ts)` - 检查是否已过期
- `is_new_day(last_date)` - 检查是否是新的一天

#### 使用示例
```python
# 设置过期时间
expires_at = get_expiry_timestamp(5)  # 5小时后

# 检查过期
if is_expired(player.expires_at_ts):
    # 清理过期玩家
    pass

# 午夜重置检查
if is_new_day(chat_state.last_midnight_reset_date):
    # 清空报名池
    pass
```

### lock_utils (锁工具)

#### 核心类与函数
- `LockManager` - 锁管理器类
  - `get_chat_lock(chat_id)` - 获取群组级锁
  - `clear_lock(chat_id)` - 清除群组锁
- `get_chat_lock(chat_id)` - 便捷函数（推荐使用）

#### 使用示例
```python
# 获取群组锁
lock = await get_chat_lock(chat_id)

# 使用上下文管理器
async with lock:
    # 临界区代码
    pass
```

## 关键依赖与配置

### 依赖
- `time` 标准库: 时间戳获取
- `datetime` 标准库: 日期时间处理
- `asyncio` 标准库: 异步锁

### 配置
工具层无配置依赖，纯函数式实现。

## 数据模型

### 时间格式
- **时间戳**: Unix 时间戳（秒，int 类型）
- **日期字符串**: YYYY-MM-DD 格式（如 "2026-02-23"）
- **时间字符串**: HH:MM 格式（如 "20:34"）
- **剩余时间**: 人类可读格式（如 "4h后"、"30min后"）

### 锁管理
- **锁类型**: `asyncio.Lock`
- **锁粒度**: 群组级（每个 chat_id 独立锁）
- **锁存储**: 全局字典 `_locks: Dict[str, asyncio.Lock]`

## 测试与质量

### 测试建议
- **时间工具**: 测试边界情况（午夜、跨天、时区）
- **锁工具**: 测试并发创建、锁的隔离性

### 性能考虑
- 时间函数：O(1) 复杂度
- 锁获取：首次创建需要全局锁，后续 O(1)

## 常见问题 (FAQ)

### Q: 为什么时间戳使用秒而不是毫秒？
A: Python 的 `time.time()` 返回秒级浮点数，转换为整数秒足够满足业务需求（分钟级精度）。

### Q: 锁管理器为什么使用全局实例？
A: 保证整个应用共享同一套锁，避免不同模块创建重复锁导致并发问题。

### Q: 如何清理不再使用的锁？
A: 调用 `_lock_manager.clear_lock(chat_id)`，但需谨慎使用，确保没有协程持有该锁。

## 相关文件清单

```
utils/
├── __init__.py          # 模块初始化
├── time_utils.py        # 时间工具（102行）
└── lock_utils.py        # 锁管理工具（59行）
```

---

**模块路径**: `astrbot_plugin_honor_of_kings_inhouse/utils/`
**工具函数数**: 10+
