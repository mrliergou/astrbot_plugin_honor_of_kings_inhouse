[根目录](../CLAUDE.md) > **repositories**

# 仓储层模块

> 数据持久化与并发控制层，负责状态管理、文件 I/O 和锁机制

## 变更记录 (Changelog)

### 2026-02-23 20:34:56
- 初始化仓储层文档

---

## 模块职责

仓储层是基础设施层的核心，负责：
- 全局状态的加载与保存
- 原子写入与备份恢复
- 群组级并发控制
- 数据完整性保障

## 入口与启动

仓储层通过单例模式初始化：

```python
from ..repositories.state_repository import get_repository

# 获取全局仓储实例
repository = get_repository()
```

## 对外接口

### StateRepository

#### 核心方法
- `load()` - 加载全局状态（支持备份恢复）
- `save(state)` - 保存全局状态（原子写入）
- `get_chat_state(chat_id)` - 获取群组状态（不存在则创建）
- `update_chat_state(chat_id, chat_state)` - 更新群组状态并持久化
- `with_chat_lock(chat_id)` - 获取群组级锁的上下文管理器
- `snapshot(chat_id)` - 获取群组状态快照（只读）

#### 使用示例
```python
# 获取锁并更新状态
async with await repository.with_chat_lock(chat_id):
    chat_state = await repository.get_chat_state(chat_id)
    # 修改 chat_state
    await repository.update_chat_state(chat_id, chat_state)
```

## 关键依赖与配置

### 依赖
- `models.py`: GlobalState、ChatState 数据模型
- `schemas.py`: 序列化/反序列化函数
- `utils.lock_utils`: 锁管理器
- `asyncio`: 异步锁机制
- `pathlib`: 文件路径处理

### 配置
- `data_dir`: 数据目录路径（默认 "data"）
- 文件命名：
  - 主文件: `hok_inhouse_state.json`
  - 临时文件: `hok_inhouse_state.json.tmp`
  - 备份文件: `hok_inhouse_state.json.bak`

## 数据模型

### 持久化结构
```json
{
  "version": 1,
  "generated_at_ts": 1708704896,
  "chats": {
    "chat_123": {
      "chat_id": "chat_123",
      "signup_pool": { ... },
      "history": [ ... ],
      "pending_archive_match_id": null,
      "config": { ... },
      "last_midnight_reset_date": "2026-02-23"
    }
  }
}
```

### 原子写入流程
1. 序列化状态为 JSON
2. 写入临时文件 `.tmp`
3. 备份旧文件到 `.bak`
4. 原子替换：`os.replace(tmp, main)`

### 备份恢复机制
- 主文件损坏 → 尝试加载备份文件
- 备份文件可用 → 恢复并重新保存主文件
- 两者都不可用 → 初始化空状态

## 测试与质量

### 并发安全
- 全局状态锁：`_state_lock` 保护加载/保存操作
- 群组级锁：每个 `chat_id` 独立锁，避免跨群组阻塞

### 测试建议
- 并发写入测试：多协程同时修改不同群组
- 文件损坏恢复测试：模拟主文件损坏场景
- 原子性测试：写入过程中断电/崩溃的恢复

## 常见问题 (FAQ)

### Q: 为什么使用 JSON 而不是数据库？
A:
- 数据量小（单群组 < 1MB）
- 部署简单，无需额外依赖
- 原子写入足以保证一致性

### Q: 如何处理大量群组的性能问题？
A:
- 当前设计：全量加载到内存
- 优化方案：按需加载群组状态（需重构）
- 阈值：建议 < 1000 个活跃群组

### Q: 锁的粒度为什么是群组级？
A:
- 避免全局锁导致的性能瓶颈
- 不同群组的操作可并发执行
- 单群组内的操作串行化保证一致性

## 相关文件清单

```
repositories/
├── __init__.py              # 模块初始化
└── state_repository.py      # 状态仓储实现（199行）
```

---

**模块路径**: `astrbot_plugin_honor_of_kings_inhouse/repositories/`
**核心类**: StateRepository
