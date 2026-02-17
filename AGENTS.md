# AGENTS.md

本文件定义在本仓库中执行开发、Issue 分析、PR 审查时的统一行为准则。

## 1. 项目概述

Daily Stock Analysis 是一个基于 AI 大模型的 A股/港股/美股自选股智能分析系统，每日自动分析并推送「决策仪表盘」到企业微信/飞书/Telegram/邮箱。

### 技术栈

| 类型 | 支持 |
|------|------|
| AI 模型 | Gemini（免费）、OpenAI 兼容、DeepSeek、通义千问、Claude、Ollama |
| 行情数据 | Efinance、AkShare、Tushare、Pytdx、Baostock、YFinance |
| Web 框架 | FastAPI + Uvicorn |
| 前端 | React + TypeScript + Vite (`apps/dsa-web/`) |
| 数据库 | SQLite (SQLAlchemy ORM) |

### 项目结构

```
daily_stock_analysis/
├── main.py              # 主入口程序
├── src/                 # 核心业务逻辑
│   ├── core/            # 管道、回测引擎、配置管理
│   ├── services/        # 业务服务层
│   ├── repositories/    # 数据访问层
│   ├── analyzer.py      # AI 分析器
│   ├── notification.py  # 通知服务
│   └── config.py        # 配置管理
├── api/                 # FastAPI Web 接口
│   ├── v1/endpoints/    # API 端点
│   └── v1/schemas/      # 请求/响应模型
├── data_provider/       # 数据源获取器
├── bot/                 # 聊天机器人命令
│   ├── commands/        # 命令处理器
│   └── platforms/       # 平台适配器
├── tests/               # 测试用例
├── apps/dsa-web/        # 前端 React 应用
└── docs/                # 文档
```

## 2. 构建/测试命令

### 后端开发

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env && vim .env

# 语法检查
python -m py_compile main.py src/config.py src/analyzer.py src/notification.py
python -m py_compile src/storage.py src/scheduler.py src/search_service.py
python -m py_compile data_provider/*.py

# Lint 检查（仅严重错误）
flake8 . --select=E9,F63,F7,F82 --max-line-length=120

# 完整 Lint
flake8 . --max-line-length=120

# 运行离线测试
python -m pytest -m "not network" -v

# 运行单个测试文件
python -m pytest tests/test_storage.py -v

# 运行单个测试函数
python -m pytest tests/test_backtest_service.py::BacktestServiceTestCase::test_run_backtest -v

# CI 门禁脚本
./scripts/ci_gate.sh

# 快速测试脚本
./test.sh syntax      # 语法检查
./test.sh code        # 代码识别测试
./test.sh yfinance    # YFinance 转换测试
./test.sh quick       # 单股快速测试
```

### 运行服务

```bash
# 运行单次分析
python main.py

# 启动 Web 界面
python main.py --webui

# 仅启动 API 服务
python main.py --serve-only --port 8000

# 定时任务模式
python main.py --schedule

# 仅大盘复盘
python main.py --market-review
```

### 前端开发

```bash
cd apps/dsa-web
npm ci
npm run lint
npm run build
```

## 3. 代码风格指南

### 通用原则

- Python 版本：3.10+
- 行宽：120 字符
- 格式化：`black` + `isort`
- Lint：`flake8`
- 注释：新增或修改的代码注释必须使用英文

### 导入顺序

```python
# 1. 标准库
import os
import sys
from typing import List, Optional

# 2. 第三方库
import pandas as pd
from fastapi import APIRouter

# 3. 本地模块
from src.config import get_config, Config
from data_provider.base import DataFetcherManager
```

### 命名规范

| 类型 | 风格 | 示例 |
|------|------|------|
| 函数 | snake_case | `get_stock_data`, `run_analysis` |
| 类 | PascalCase | `StockAnalyzer`, `NotificationService` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRIES`, `DEFAULT_TIMEOUT` |
| 私有方法 | _leading_underscore | `_fetch_data`, `_parse_response` |

### 类型注解

```python
def analyze_stock(code: str, days: int = 30) -> Optional[AnalysisResult]:
    """Analyze a stock and return the result."""
    pass

def get_stocks() -> List[str]:
    """Get list of stock codes."""
    return config.stock_list
```

### 错误处理

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def fetch_data(code: str):
    try:
        # Implementation
        pass
    except RateLimitError:
        logger.warning(f"Rate limited for {code}")
        raise
```

## 4. 模块依赖关系

```
main.py
├── src/core/pipeline.py          # 分析管道
│   ├── src/analyzer.py           # AI 分析
│   ├── src/stock_analyzer.py     # 股票分析
│   ├── src/market_analyzer.py    # 大盘分析
│   ├── src/notification.py       # 通知推送
│   ├── src/search_service.py     # 新闻搜索
│   └── data_provider/            # 行情数据
│
├── api/app.py                    # FastAPI 应用
│   ├── api/v1/endpoints/         # API 端点
│   └── static/                   # 前端静态文件
│
└── bot/dispatcher.py             # 机器人命令分发
    ├── bot/commands/             # 命令处理器
    └── bot/platforms/            # 平台适配器
```

## 5. 子模块 AGENTS.md

各子模块有独立的 AGENTS.md 文件，包含详细的模块说明：

| 模块 | 文件 | 说明 |
|------|------|------|
| `src/` | [AGENTS.md](src/AGENTS.md) | 核心业务逻辑 |
| `api/` | [AGENTS.md](api/AGENTS.md) | FastAPI Web 接口 |
| `data_provider/` | [AGENTS.md](data_provider/AGENTS.md) | 数据源获取器 |
| `bot/` | [AGENTS.md](bot/AGENTS.md) | 聊天机器人命令 |
| `tests/` | [AGENTS.md](tests/AGENTS.md) | 测试用例 |

## 6. 通用协作原则

- 配置约束：统一使用 `.env`（参见 `.env.example`）
- 代码质量：优先保证可运行、可回归验证、可追踪（日志/错误信息清晰）
- Git 约束：
  - 未经明确确认，不执行 `git commit`
  - commit message 不添加 `Co-Authored-By`
  - 后续所有 commit message 必须使用英文

## 7. Issue 分析原则

每个 Issue 必须先回答 3 个问题：

1. 是否合理（Reasonable）
- 是否描述了真实影响（功能错误、数据错误、性能/稳定性问题、体验退化）
- 是否有可验证证据（日志、截图、复现步骤、版本信息）
- 是否与项目目标相关（股票分析、数据源、通知、API/WebUI、部署链路）

2. 是否是 Issue（Valid Issue）
- 属于缺陷/功能缺失/回归/文档错误之一，而非纯咨询或环境误用
- 能定位到仓库责任边界；若是三方服务波动，也需判断是否需要仓库侧兜底
- 如果是使用问题，应转为文档改进或 FAQ，而不是代码缺陷

3. 是否好解决（Solvability）
- 可否稳定复现
- 依赖是否可控（第三方 API、网络、权限、密钥）
- 变更范围与风险等级（低/中/高）
- 是否存在临时缓解方案（降级、兜底、开关、重试、回退策略）

### Issue 结论模板

- 结论：`成立 / 部分成立 / 不成立`
- 分类：`bug / feature / docs / question / external`
- 优先级：`P0 / P1 / P2 / P3`
- 难度：`easy / medium / hard`
- 建议：`立即修复 / 排期修复 / 文档澄清 / 关闭`

## 8. PR 分析原则

每个 PR 需按以下顺序审查：

1. 必要性（Necessity）
- 是否解决明确问题，或提供明确业务价值
- 是否避免"为了改而改"的重构

2. 关联性（Traceability）
- 是否关联对应 Issue（建议必须有：`Fixes #xxx` 或 `Refs #xxx`）
- 若无 Issue，PR 描述必须给出动机、场景与验收标准

3. 类型判定（Type）
- 明确标注：`fix / feat / refactor / docs / chore / test`
- 对"fix/bug"类 PR：必须说明原问题、根因、修复点、回归风险

4. 描述完整性（Description Completeness）
- 必须包含：
  - 背景与问题
  - 变更范围（改了哪些模块）
  - 验证方式与结果（命令、关键输出）
  - 兼容性与破坏性变更说明（如有）
  - 回滚方案（至少一句）
  - 若为 issue 修复：在 PR description 中显式写明关闭语句（如 `Fixes #241` / `Closes #241`）

5. 合入判定（Merge Readiness）
- 可直接合入（Ready to Merge）条件：
  - 目标明确且必要
  - 有 Issue 或同等质量的问题描述
  - 变更与描述一致，无隐藏副作用
  - 关键验证已通过（语法/测试/关键链路）
  - 无阻断性风险（安全、数据损坏、明显性能回退）
- 不可直接合入（Not Ready）条件：
  - 描述不完整，无法确认动机和影响
  - 无验证证据
  - 引入明显风险且无回滚策略
  - 与仓库方向无关或重复实现

## 9. 交付与发布同步原则

- 功能开发、缺陷修复完成后，必须同步更新文档：
  - `README.md`（用户可见能力、使用方式、配置项变化）
  - `docs/CHANGELOG.md`（版本变更记录、影响范围、兼容性说明）
- 发布语义必须与改动规模匹配，在提交说明中添加对应 tag 标签：
  - `#patch`：修复类、小改动
  - `#minor`：新增可用功能、向后兼容
  - `#major`：破坏性变更或重大架构调整
  - `#skip` / `#none`：明确不触发自动版本标签
- 若改动用于解决已有 issue，PR description 必须声明关闭该 issue（`Fixes #xxx` / `Closes #xxx`），避免修复完成后 issue 悬挂

## 10. 建议评审输出格式

### Issue 评审输出

- `是否合理`：是/否 + 理由
- `是否是 issue`：是/否 + 理由
- `是否好解决`：是/否 + 难点
- `建议动作`：修复/排期/文档/关闭

### PR 评审输出

- `必要性`：通过/不通过
- `是否有对应 issue`：有/无（编号）
- `PR 类型`：fix/feat/...
- `description 完整性`：完整/不完整（缺失项）
- `是否可直接合入`：可/不可 + 必改项
