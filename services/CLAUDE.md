[根目录](../CLAUDE.md) > **services**

# 服务层模块

> 业务逻辑封装层，提供报名、分组、历史统计和权限管理功能

## 变更记录 (Changelog)

### 2026-02-23 20:34:56
- 初始化服务层文档

---

## 模块职责

服务层是业务逻辑的核心实现层，负责：
- 协调领域模型与基础设施层
- 实现业务规则与流程控制
- 提供统一的业务接口给表现层

## 入口与启动

服务层由插件入口 `main.py` 实例化并调用：

```python
# 在 HonorOfKingsInhousePlugin.__init__ 中初始化
self.signup_service = SignupService()
self.grouping_service = GroupingService()
self.history_service = HistoryService()
self.auth_service = AuthService()
```

## 对外接口

### SignupService (报名服务)
- `register()` - 玩家报名（支持随机/智能模式）
- `cancel()` - 取消报名
- `list_board()` - 获取报名看板
- `cleanup_expired()` - 清理过期报名

### GroupingService (分组服务)
- `random_group()` - 随机分组（10人）
- `smart_group()` - 智能分组（根据偏好）
- `archive_match()` - 归档对局结果

### HistoryService (历史服务)
- `query_matches()` - 查询历史对局
- `win_rate()` - 胜率统计

### AuthService (权限服务)
- `is_admin()` - 检查管理员权限
- `add_admin()` - 添加管理员
- `remove_admin()` - 移除管理员

## 关键依赖与配置

### 依赖注入
所有服务通过 `get_repository()` 获取仓储实例：
```python
from ..repositories.state_repository import get_repository

class SignupService:
    def __init__(self):
        self.repository = get_repository()
```

### 配置项
服务层读取 `ChatConfig` 中的配置：
- `ttl_hours`: 报名过期时间（默认 5 小时）
- `max_history`: 最大历史记录数（默认 500）
- `admin_users`: 管理员用户列表
- `algorithm`: 默认分组算法（默认 "mcmf"）

## 数据模型

### 输入模型
- `Player` - 玩家实体（来自 `models.py`）
- `SignupPool` - 报名池
- `ChatState` - 群组状态

### 输出模型
- `SignupResult` - 报名结果（包含成功标志和消息）
- `GroupingResult` - 分组结果（包含对局ID）
- `HistoryResult` - 历史查询结果
- `ArchiveResult` - 归档结果

## 测试与质量

### 当前状态
- 无单元测试
- 依赖集成测试与日志

### 测试建议
- 报名服务：测试过期清理、午夜重置逻辑
- 分组服务：测试人数校验、算法调用
- 历史服务：测试数据聚合与格式化
- 权限服务：测试权限检查逻辑

## 常见问题 (FAQ)

### Q: 如何添加新的服务方法？
A: 在对应服务类中添加 `async` 方法，使用 `async with await self.repository.with_chat_lock(chat_id)` 保证并发安全。

### Q: 服务层如何处理异常？
A: 抛出 `errors.py` 中定义的业务异常（如 `InsufficientPlayersError`），由表现层捕获并转换为用户消息。

### Q: 为什么所有方法都是 async？
A: 因为涉及文件 I/O（持久化）和锁操作，必须使用异步以避免阻塞事件循环。

## 相关文件清单

```
services/
├── __init__.py              # 模块初始化
├── signup_service.py        # 报名服务（384行）
├── grouping_service.py      # 分组服务（315行）
├── history_service.py       # 历史服务（78行）
└── auth_service.py          # 权限服务（54行）
```

---

**模块路径**: `astrbot_plugin_honor_of_kings_inhouse/services/`
**总代码量**: ~831 行
