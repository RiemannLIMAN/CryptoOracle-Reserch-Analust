# Changelog / 变更日志

All notable changes to this project will be documented in this file.

## [0.2.0] - 2025-12-22

### 🇬🇧 English Version

#### ✨ New Features
*   **🤖 Paper Trading System**: Introduced a fully automated paper trading module (`src/analysis/paper_trader.py`).
    *   **Virtual Portfolio**: Manages a simulated 10,000 USDT balance with persistent storage in `data/paper_trading.json`.
    *   **AI Decision Making**: AI now generates actionable trade signals (BUY/SELL/HOLD) based on market analysis and current portfolio status.
    *   **Performance Tracking**: Weekly reports on total asset value and ROI are appended to notifications.
*   **📉 Funding Rate Analysis**:
    *   Added `get_funding_rates()` to `OKXClient` to fetch real-time funding rates for top coins (BTC, ETH, SOL, DOGE).
    *   Updated `LLMClient` prompts to interpret funding rates as market sentiment indicators (e.g., crowded longs vs. short squeezes).

#### 📚 Documentation
*   **Git Guide**: Added `docs/GIT_GUIDE.md` for version control best practices.
*   **Readme Update**: Moved `README.md` to project root and updated "Support & Contribution" section.

---

### 🇨🇳 中文版本

#### ✨ 新特性
*   **🤖 模拟盘回测系统**: 新增全自动模拟交易模块 (`src/analysis/paper_trader.py`)。
    *   **虚拟账户**: 管理 10,000 USDT 初始资金，数据持久化存储于 `data/paper_trading.json`。
    *   **AI 交易决策**: AI 基于研报和当前持仓，自动生成买卖指令 (BUY/SELL/HOLD)。
    *   **业绩追踪**: 每次通知自动附带模拟盘周报（总资产、收益率）。
*   **📉 资金费率分析**:
    *   `OKXClient` 新增 `get_funding_rates()` 接口，实时抓取主流币（BTC, ETH 等）的资金费率。
    *   更新了 AI Prompt，使其能根据费率正负值判断市场多空拥挤度。

#### 📚 文档
*   **Git 指南**: 新增 `docs/GIT_GUIDE.md`，规范版本控制流程。
*   **README 更新**: 将 `README.md` 移至项目根目录，并新增“支持与贡献”板块。

## [0.1.0] - 2025-12-20

### 🇬🇧 English Version

#### ✨ Features
*   **DeepSeek-R1 Integration**: Updated default model to `deepseek-reasoner` in `.env` for advanced Chain-of-Thought (CoT) reasoning.
*   **Startup Banner**: Added a rich terminal welcome panel displaying version, author, and startup time via `src/main.py`.
*   **Immediate Execution**: Scheduler now triggers an immediate analysis task upon startup before entering the interval loop.

#### 🎨 UI/UX Improvements
*   **Mobile-Friendly Notifications**:
    *   Refactored Feishu/DingTalk notifications in `src/utils/notifier.py`.
    *   Automatically converts wide Markdown tables into vertical **List Views** for better mobile readability.
    *   Added visual separators and a professional footer signature.
*   **Clean Console Logs**:
    *   Simplified console output by removing timestamps/metadata (full details kept in file logs).
    *   Silenced `pip install` output in startup scripts (`run.bat`, `run.sh`).
    *   Downgraded verbose API/LLM initialization logs from `INFO` to `DEBUG`.

#### 🐛 Bug Fixes & Engineering
*   **Virtual Env Logic**: 
    *   `run.sh` now detects existing virtual environments (e.g., Conda) and skips redundant creation/activation.
    *   Fixed incorrect `deactivate` behavior when exiting.
*   **Dependency Path**: Moved `requirements.txt` to the project root directory and removed unused `openai` dependency.
*   **Git Ignore**: Added `okx_research/` to `.gitignore` to prevent committing local environments.

#### 📚 Documentation
*   **License**: Adopted **CC BY-NC-SA 4.0** license (Attribution-NonCommercial-ShareAlike).
*   **README Overhaul**: Complete rewrite with clearer value propositions, workflow diagrams, streamlined "Quick Start" guide, and removed redundant badges.

---

### 🇨🇳 中文版本

#### ✨ 新特性
*   **DeepSeek-R1 集成**: 将 `.env` 中的默认模型更新为 `deepseek-reasoner`，启用 AI 的深度思维链推理能力。
*   **启动画面**: 在 `src/main.py` 中新增了基于 Rich 的终端欢迎面板，显示版本号、作者及启动时间。
*   **立即执行**: 优化了调度器逻辑，程序启动后会立即执行一次分析任务，无需等待第一个定时周期。

#### 🎨 体验优化
*   **移动端通知适配**:
    *   重构了 `src/utils/notifier.py` 中的飞书/钉钉通知逻辑。
    *   将 Markdown 宽表格自动转换为垂直的 **列表视图**，解决了手机端阅读需要左右滑动的问题。
    *   增加了视觉分割线和底部机器署名。
*   **纯净日志**:
    *   `src/utils/logger.py`: 简化控制台输出，移除了冗余的时间戳（文件日志中依然保留完整信息）。
    *   启动脚本 (`run.bat`, `run.sh`) 中的 `pip install` 调整为静默模式，减少刷屏。
    *   将 API 请求和 LLM 初始化等啰嗦日志的级别从 `INFO` 降级为 `DEBUG`。

#### 🐛 修复与工程
*   **虚拟环境逻辑**: 
    *   `run.sh` 现在能智能检测当前环境（如 Conda），如果已在环境中则跳过创建 `okx_research` 环境。
    *   修复了脚本退出时错误执行 `deactivate` 的问题。
*   **依赖管理**: 将 `requirements.txt` 从 `src/` 移至项目根目录，并移除了未使用的 `openai` 库。
*   **Git 配置**: 在 `.gitignore` 中忽略了本地生成的 `okx_research/` 虚拟环境目录。

#### 📚 文档
*   **许可证**: 正式采用 **CC BY-NC-SA 4.0** (署名-非商业性使用-相同方式共享) 协议。
*   **README 重构**: 全面更新文档，强调核心价值，优化“快速开始”流程，更新目录结构图，并移除了冗余的徽章。
