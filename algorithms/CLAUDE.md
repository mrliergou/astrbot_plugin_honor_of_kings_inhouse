[根目录](../CLAUDE.md) > **algorithms**

# 算法层模块

> 分组算法实现层，提供随机分组、贪心回溯和最小费用最大流算法

## 变更记录 (Changelog)

### 2026-02-23 20:34:56
- 初始化算法层文档

---

## 模块职责

算法层是纯函数式的计算模块，负责：
- 实现不同的分组策略
- 保证位置覆盖与偏好匹配
- 提供可插拔的算法接口

## 入口与启动

算法模块由 `GroupingService` 调用：

```python
from ..algorithms.random_grouping import random_group
from ..algorithms.greedy_backtracking import greedy_backtracking_group
from ..algorithms.min_cost_flow import min_cost_flow_group

# 根据配置选择算法
if algorithm == "greedy":
    red_team, blue_team = greedy_backtracking_group(players)
else:  # mcmf
    red_team, blue_team = min_cost_flow_group(players)
```

## 对外接口

### random_group()
**签名**: `random_group(players: List[Player]) -> Tuple[TeamAssignment, TeamAssignment]`

**功能**: 将10名玩家随机分配到红蓝两队，每队5人，随机分配位置。

**算法**:
1. 随机打乱玩家列表
2. 前5人分配到红方，后5人分配到蓝方
3. 随机分配5个位置

### greedy_backtracking_group()
**签名**: `greedy_backtracking_group(players: List[Player]) -> Tuple[TeamAssignment, TeamAssignment]`

**功能**: 使用贪心+回溯策略进行智能分组。

**算法**:
1. 优先锁定唯一位置的玩家
2. 贪心分配多选玩家
3. 1-2步回溯优化
4. 随机模式玩家填充空缺

### min_cost_flow_group()
**签名**: `min_cost_flow_group(players: List[Player]) -> Tuple[TeamAssignment, TeamAssignment]`

**功能**: 使用最小费用最大流算法（简化版）进行智能分组。

**算法**:
1. 构建费用矩阵（第一偏好10分、第二偏好5分、随机3分、非偏好1分）
2. 多次随机采样（20次 Monte Carlo）
3. 贪心选择最高得分的（玩家、位置、队伍）组合
4. 评分选优，返回最佳方案

**注意**: 这是简化实现，真正的 MCMF 需要网络流算法库。

## 关键依赖与配置

### 依赖
- `models.py`: Player、TeamAssignment 数据模型
- `constants.py`: Role、TeamSide、SignupMode 枚举
- `random` 标准库: 随机化与采样

### 配置
算法层无配置依赖，纯函数式实现。

## 数据模型

### 输入
- `List[Player]`: 必须是10人的玩家列表

### 输出
- `Tuple[TeamAssignment, TeamAssignment]`: 红方和蓝方的分配结果

### 异常
- `ValueError`: 玩家数量不是10人或无法完成分配

## 测试与质量

### 测试建议
- **随机分组**: 测试输出的随机性和完整性
- **贪心回溯**: 测试边界情况（全部冲突、部分冲突）
- **MCMF**: 测试评分函数、采样次数对结果的影响

### 性能指标
- 随机分组: O(1)
- 贪心回溯: O(n²) ~ O(n³)
- MCMF 简化版: O(20 × n²) ≈ O(n²)

## 常见问题 (FAQ)

### Q: 为什么 MCMF 是简化版？
A: 真正的 MCMF 需要构建网络流图并使用 Bellman-Ford 或 Dijkstra 算法求解，实现复杂度高。当前版本使用贪心+采样模拟效果。

### Q: 如何添加新算法？
A:
1. 在 `algorithms/` 下创建新文件（如 `genetic_algorithm.py`）
2. 实现函数签名：`def xxx_group(players: List[Player]) -> Tuple[TeamAssignment, TeamAssignment]`
3. 在 `GroupingService` 中添加调用分支

### Q: 算法如何保证公平性？
A:
- 随机分组：完全随机，无偏好
- 智能分组：最大化偏好命中率，平衡两队的总偏好分

## 相关文件清单

```
algorithms/
├── __init__.py                  # 模块初始化
├── random_grouping.py           # 随机分组算法
├── greedy_backtracking.py       # 贪心回溯算法
└── min_cost_flow.py             # 最小费用最大流算法（175行）
```

---

**模块路径**: `astrbot_plugin_honor_of_kings_inhouse/algorithms/`
**核心算法**: 3个
