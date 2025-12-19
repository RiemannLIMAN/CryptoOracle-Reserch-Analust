# 🏗️ 系统架构文档 (System Architecture)

本文档旨在为开发者和高级用户提供 OKX Research Analyst 的技术架构视图，帮助您理解系统的内部工作原理、数据流向及模块交互。

---

## 1. 🗺️ 总体架构图 (High-Level Architecture)

系统采用 **🧩 模块化 (Modular)** 和 **🍰 分层 (Layered)** 设计，主要分为四层：

```mermaid
graph TD
    User[用户/调度器] --> Main[入口层 (Main Entry)]
    
    subgraph Core [核心业务层]
        Main --> DataProc[数据处理 (Data Processing)]
        Main --> Analysis[分析引擎 (Analysis Engine)]
        Main --> Notify[通知服务 (Notification)]
    end
    
    subgraph Modules [功能模块层]
        DataProc --> OKX_Client[OKX API Client]
        Analysis --> Fund_Analyzer[基本面分析 (Fundamental)]
        Analysis --> Tech_Analyzer[技术分析 (Technical)]
        Analysis --> LLM_Client[LLM Client (DeepSeek/OpenAI)]
        Fund_Analyzer -.-> LLM_Client
    end
    
    subgraph Infra [基础设施层]
        Config[配置管理 (Settings & Env)]
        Logger[日志系统 (Logging)]
        Cache[本地缓存 (JSON/Memory)]
    end
    
    Modules --> Infra
```

---

## 2. 🧱 核心模块详解

### 2.1 🚪 入口层 (Entry Point)
*   **📂 文件**: `src/main.py`
*   **🎯 职责**: 
    *   程序的启动入口。
    *   负责初始化各个单例模块（Logger, Clients）。
    *   解析命令行参数。
    *   管理调度器 (`schedule` 库) 的生命周期。
    *   协调“获取数据 -> 分析 -> 推送”的流水线。
    *   使用 `Rich` 库渲染终端 UI。

### 2.2 📡 数据获取层 (Data Acquisition)
*   **📂 文件**: `src/api/okx_client.py`
*   **🎯 职责**:
    *   封装 OKX V5 REST API。
    *   处理网络请求的重试与超时。
    *   将原始 JSON 数据转换为 Pandas DataFrame，方便后续处理。
    *   **🔑 关键方法**: `get_tickers()` 获取市场行情。

### 2.3 🧠 分析引擎层 (Analysis Engine)
这是系统的核心大脑，包含三个子模块：

1.  **📊 基本面分析器 (`src/analysis/fundamental.py`)**:
    *   **🎯 职责**: 识别币种所属赛道（Sector），管理币种的基础信息。
    *   **⚙️ 机制**: 采用三级缓存策略获取赛道信息：
        1.  内存缓存 (Memory Cache)
        2.  本地文件 (`config/coins_data.json`)
        3.  LLM 实时查询 (作为兜底)
    *   **✨ AI 增强**: `update_sectors_with_ai()` 方法会批量调用 LLM 识别未知币种的赛道。

2.  **📈 技术分析器 (`src/analysis/technical.py`)**:
    *   **🎯 职责**: 计算纯数学指标。
    *   **📐 指标**: 24h 涨跌幅、波动率等。

3.  **🤖 LLM 客户端 (`src/api/llm_client.py`)**:
    *   **🎯 职责**: 与大模型（DeepSeek, OpenAI）交互。
    *   **🎨 Prompt 工程**: 内部维护了 `system_prompt`，确保输出格式统一（Markdown 表格、摘要）。
    *   **🔌 兼容性**: 自动适配不同的 API 路径格式 (`/v1/chat/completions`)。

### 2.4 📢 展示与通知层 (Presentation & Notification)
*   **📂 文件**: `src/utils/notifier.py`
*   **🎯 职责**:
    *   格式化分析结果。
    *   分发消息到不同的 Webhook 渠道（飞书、钉钉）。
    *   处理消息发送失败的异常。

---

## 3. 🌊 数据流向 (Data Flow)

一次完整的分析任务 (`run_analysis_task`) 数据流如下：

1.  **🌱 初始化**: 加载 `.env` 配置，初始化 Logger。
2.  **🎣 数据拉取**: `OKXClient` 请求 OKX 接口，返回 Top 交易量的币种列表 (DataFrame)。
3.  **✨ 数据增强**:
    *   `FundamentalAnalyzer` 遍历币种列表。
    *   检查本地缓存是否有赛道信息。
    *   如果没有，调用 `LLMClient` 询问 "PEPE 是什么板块？"，并更新缓存。
    *   将赛道信息合并回 DataFrame。
4.  **📝 Prompt 构建**: 将增强后的数据格式化为文本摘要（包含价格、涨跌幅、赛道）。
5.  **🧠 AI 推理**:
    *   构建 Prompt: "基于以下数据，分析市场情绪..."
    *   发送给 LLM。
6.  **📤 结果输出**:
    *   终端: 使用 `Rich` 渲染 Markdown。
    *   推送: `Notifier` 发送 Webhook 请求。

---

## 4. 📂 目录结构说明

```text
OKXResearch_Analyst/
├── config/                 # [⚙️ 配置层]
│   ├── settings.py         # 环境变量加载与路径计算
│   └── coins_data.json     # 静态知识库 (赛道映射)
├── data/                   # [💾 数据层] (预留，用于存储历史CSV)
├── docs/                   # [📚 文档层]
├── logs/                   # [🪵 日志层] 运行时产生的日志文件
├── src/                    # [💻 源码层]
│   ├── analysis/           # 分析逻辑 (基本面/技术面)
│   ├── api/                # 外部接口适配器 (OKX/LLM)
│   ├── utils/              # 通用工具 (日志/通知)
│   └── main.py             # 主程序
├── tests/                  # [🧪 测试层] 单元测试
├── .env                    # [🔐 敏感配置] API Key (不提交 Git)
├── Dockerfile              # [🐳 部署] Docker 构建文件
└── requirements.txt        # Python 依赖
```

## 5. 🔌 扩展性设计

*   **➕ 添加新交易所**: 只需在 `src/api/` 下新增 `binance_client.py` 并实现类似的 `get_tickers()` 方法。
*   **🔄 更换 AI 模型**: 修改 `.env` 配置即可，底层 `LLMClient` 采用通用的 OpenAI 协议。
*   **📡 新增通知渠道**: 在 `Notifier` 类中添加新的发送方法（如 Telegram, Slack）。
