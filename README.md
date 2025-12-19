# 🚀 OKX Research Analyst (AI Co-Pilot)

> **"数据驱动决策，AI 洞察未来"**  
> 结合 **OKX 交易所** 的深度流动性数据与 **DeepSeek-R1** 的逻辑推理能力，为您打造机构级的加密货币投研助理。

## 💡 核心价值
- **全自动**：从数据抓取到研报生成，无需人工干预
- **深度推理**：基于 DeepSeek-R1 的思维链分析，拒绝浅层涨跌描述
- **多端推送**：手机端实时接收高价值投研信息


---

## 📖 简介 (Introduction)

**OKX Research Analyst** 是一个专为加密货币交易者、量化研究员和社区运营者设计的**全自动化投研系统**。

在瞬息万变的加密市场中，信息过载是最大的痛点。本系统不仅仅是一个简单的行情抓取脚本，它更像是一个不知疲倦的**初级研究员**，能够 24/7 全天候执行以下工作流：

1.  **🎣 实时捕获**: 直连 OKX V5 API，毫秒级获取全市场数千个交易对的量价数据。
2.  **🧹 智能清洗**: 自动过滤流动性差的“僵尸币”，聚焦 Top 30 资金最活跃的核心资产。
3.  **🧠 深度推理**: 引入 **DeepSeek-R1 (Reasoner)** 模型，利用思维链 (CoT) 技术，对市场数据进行深度逻辑归因（而非简单的涨跌描述）。
4.  **📝 研报生成**: 自动产出包含“核心摘要”、“板块轮动分析”、“风险提示”的结构化 Markdown 研报。
5.  **📢 多端触达**: 通过飞书/钉钉机器人，将高价值信息实时推送到您的手机端。

无论您是需要每日早报的交易员，还是寻找阿尔法信号的量化开发者，它都能为您节省 90% 的盯盘和整理时间。

---

## 📚 文档中心 (Documentation)

我们提供了完善的文档体系，帮助您从入门到精通：

*   **[⚡ 快速上手 (USAGE.md)](docs/USAGE.md)**: 
    *   Windows/Mac/Linux 一键启动脚本 (`run.bat`, `run.sh`)
    *   后台静默运行 (守护模式)
    *   常见问题排查 (FAQ)
*   **[⚙️ 配置指南 (CONFIGURATION.md)](docs/CONFIGURATION.md)**: 
    *   `.env` 环境变量详解 (API Key, Proxy)
    *   `coins_data.json` 赛道知识库定制
*   **[🧩 架构设计 (ARCHITECTURE.md)](docs/ARCHITECTURE.md)**: 
    *   系统模块划分与数据流向
    *   二次开发指南
*   **[✨ 功能特性 (FEATURES.md)](docs/FEATURES.md)**: 
    *   核心能力与技术亮点详解
*   **[🐙 Git 指南 (GIT_GUIDE.md)](docs/GIT_GUIDE.md)**: 
    *   版本控制流程与安全规范

---

## ✨ 核心特性 (Key Features)

### 1. 🧠 深度 AI 投研 (Deep Reasoning)
*   **🧐 智能归因**: 告别“涨了因为买的人多”这种废话。DeepSeek-R1 模型会结合板块效应、资金流向进行逻辑推理。
*   **🔄 动态知识库**: 内置“三级缓存”机制 (Memory -> Local JSON -> AI Query)。遇到新上线的币种（如 PNUT），系统会自动询问 AI 并标记其赛道，无需手动更新代码。
*   **📝 结构化输出**: 研报包含 Markdown 表格、情感评分、机会/风险点列举，拒绝大段纯文本。

### 2. 📊 沉浸式终端体验 (Rich UI)
*   **🎨 现代化界面**: 使用 `Rich` 库打造，支持彩色日志、动态加载动画 (Spinner)、Markdown 渲染面板。
*   **🪵 纯净日志**: 控制台只展示关键信息，详细的调试日志 (Debug/Trace) 自动写入文件并轮转备份，保持界面清爽。

### 3. 🛡️ 企业级工程架构
*   **🧩 模块化设计**: API 层、分析层、通知层完全解耦。想换个交易所？只需重写 `okx_client.py`；想换个模型？改 `.env` 即可。
*   **⚙️ 灵活调度**: 支持 Crontab 模式（跑一次退出）和 Daemon 模式（常驻后台，每 N 分钟运行一次）。
*   **🔔 移动端适配**: 飞书/钉钉消息经过专门优化，表格自动转为列表视图，完美适配手机竖屏阅读。

---

## 🚀 快速开始 (Quick Start)

### 1. 🛠️ 环境准备
确保您的系统安装了 Python 3.8 或以上版本。

```bash
git clone https://github.com/RiemannLIMAN/CryptoOracle-Reserch.git
cd OKXResearch_Analyst
```

### 2. 🔑 配置密钥
复制配置文件模板：
```bash
cp .env.example .env
```
编辑 `.env` 文件，填入您的 DeepSeek API Key：
```ini
LLM_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
LLM_MODEL=deepseek-reasoner  # 推荐使用 R1 推理模型
```

### 3. ▶️ 一键运行
我们为您准备了全自动启动脚本，自动处理虚拟环境和依赖安装：

**Windows 用户**:
```powershell
.\run.bat
```

**Mac/Linux 用户**:
```bash
chmod +x run.sh
./run.sh
```

---

## 📂 项目结构 (Structure)

```text
OKXResearch_Analyst/
├── config/                 # ⚙️ 配置中心 (Settings & Knowledge Base)
├── docs/                   # 📚 项目文档 (Usage, Config, Arch)
├── logs/                   # 🪵 运行日志 (Auto-rotated)
├── src/                    # 💻 源代码
│   ├── analysis/           # 🧠 分析引擎 (Fundamental & Technical)
│   ├── api/                # 📡 外部接口 (OKX & LLM)
│   ├── utils/              # 🛠️ 通用工具 (Logger & Notifier)
│   └── main.py             # 🚀 程序入口
├── .env.example            # 📄 环境变量模板
├── LICENSE                 # ⚖️ 开源协议 (CC BY-NC-SA 4.0)
├── requirements.txt        # 📦 项目依赖
├── run.bat                 # 🪟 Windows 启动脚本
└── run.sh                  # 🐧 Linux/Mac 启动脚本
```

---

## 🤝 支持与贡献 (Support & Contribution)

**OKX Research Analyst** 是一个开源项目，我们需要您的力量让它变得更强！

### 如何贡献
*   **🐛 提交 Bug**：如果您发现程序报错或逻辑漏洞，请提交 Issue 并附上 `logs/okx_research.log` 中的错误堆栈。
*   **💡 功能建议**：欢迎提出新的指标算法、风控策略或交易适配请求。
*   **💻 代码提交**：Fork 本项目，创建您的 Feature 分支，并提交 Pull Request。

### 联系我们
*   **GitHub Issues**: [https://github.com/RiemannLIMAN/CryptoOracle-Reserch/issues](https://github.com/RiemannLIMAN/CryptoOracle-Reserch/issues)
*   **Email**: niudtao@163.com

### ☕ 支持作者
如果您觉得本项目对您有帮助，欢迎使用作者的 OKX 邀请码注册，这将支持 Riemann 持续维护本项目。

*   **🦄 OKX 全球邀请码**: `95572792`
*   **👉 注册链接**: [点击这里注册 OKX (免翻墙)](https://www.okx.com/join/95572792)

感谢每一位贡献者！让 AI 赋能每一个交易员。

**作者：Riemann**

---

## ⚖️ 许可证 (License)

本项目采用 **CC BY-NC-SA 4.0** 许可证（Attribution-NonCommercial-ShareAlike 4.0 International）。

这意味着您可以：
*   **共享**：在任何媒介或格式下复制和分发本素材。
*   **改编**：混合、转换或基于本素材进行创作。

**前提是您必须遵守以下条款：**
1.  **✍️ 署名 (Attribution)**：必须给出适当的署名，提供指向本许可证的链接，并说明是否做了修改。
2.  **🚫 非商业性使用 (NonCommercial)**：**不得**将本素材用于商业目的。
3.  **🔄 相同方式共享 (ShareAlike)**：如果您对本素材进行再创作，必须采用与本协议**相同**的许可证分发您的贡献。

📜 [查看完整许可证](LICENSE)

---

## ⚠️ 免责声明

本工具仅用于市场数据分析与研究验证，**不构成任何投资建议**。加密货币市场风险极高，请根据自身风险承受能力理性投资。开发者不对因使用本软件而产生的任何资金损失负责。

---

**Made with ❤️ by OKX Research Analyst Team**
