# ⚙️ 配置指南 (Configuration Guide)

欢迎使用 **OKX Research Analyst**！本文档将手把手教您如何配置这个强大的 AI 投研助手。

我们将配置分为三个层级，您可以根据需求逐步设置：

1.  **🔐 核心环境变量 (`.env`)**: 必须配置，涉及 API Key 和运行模式。
2.  **📚 知识库配置 (`coins_data.json`)**: 可选配置，用于教 AI 识别新的币种赛道。
3.  **🛠️ 底层设置 (`settings.py`)**: 开发者选项，通常无需修改。

---

## 1. 🔐 核心环境变量 (.env)

`.env` 文件是您的控制中心。请复制项目根目录下的 `.env.example` 文件并重命名为 `.env`。

> ⚠️ **安全提示**: 此文件包含您的私钥，**绝对不要**分享给他人或上传到 GitHub。

### 🧠 AI 大脑配置 (必填)

这是系统的核心，支持所有兼容 OpenAI 格式的大模型（如 DeepSeek, Moonshot, ChatGPT）。

| 变量名 | 必填 | 默认值 | 说明 |
| :--- | :---: | :--- | :--- |
| `LLM_API_KEY` | ✅ | 无 | 您的模型 API Key (例如 `sk-xxxx`)。 |
| `LLM_BASE_URL` | ❌ | `https://api.deepseek.com` | API 接口地址。支持智能补全，只需填域名即可 (如 `https://api.moonshot.cn/v1`)。 |
| `LLM_MODEL` | ❌ | `deepseek-chat` | 模型名称 (如 `moonshot-v1-8k`, `gpt-4o`)。 |

### 📡 交易所数据源 (选填)

默认连接 OKX 公共行情，通常**不需要**填 Key。仅在您需要访问私有数据或提高限频时配置。

| 变量名 | 说明 |
| :--- | :--- |
| `OKX_API_KEY` | OKX V5 API Access Key |
| `OKX_SECRET_KEY` | OKX V5 API Secret Key |
| `OKX_PASSPHRASE` | API Passphrase |
| `OKX_BASE_URL` | 默认为 `https://www.okx.com`。AWS 用户可用 `https://aws.okx.com` 加速。 |

### ⏰ 自动化与调度 (Scheduler)

决定机器人是“跑一次就歇”还是“全天候待命”。

| 变量名 | 设置建议 |
| :--- | :--- |
| `ENABLE_SCHEDULER` | `true` = 开启守护模式 (常驻后台)；`false` = 单次运行模式。 |
| `SCHEDULE_INTERVAL` | **(推荐)** 设置为 `30` 或 `60` (分钟)。每隔一段时间自动分析一次。 |
| `SCHEDULE_TIME` | 仅在 `SCHEDULE_INTERVAL=0` 时生效。设置每天固定运行时间 (如 `08:00`)。 |

### 📢 消息推送 (Notifications)

分析报告推送到哪里？

| 平台 | 变量名 | 配置说明 |
| :--- | :--- | :--- |
| **飞书** | `FEISHU_WEBHOOK_URL` | 飞书群机器人的 Webhook 地址。 |
| **钉钉** | `DINGTALK_WEBHOOK_URL` | 钉钉群机器人 Webhook。**注意**: 安全设置需勾选“自定义关键词”，并包含 `OKX` 或 `Report`。 |

---

## 2. 📚 知识库配置 (coins_data.json)

位于 `config/coins_data.json`。这是 AI 的“笔记本”，您可以随时更新它来教 AI 认识新币。

### 🏷️ 赛道映射 (sectors)

告诉 AI 哪个币属于哪个板块，这对分析“板块轮动”至关重要。

```json
"sectors": {
    "🤖 AI": ["FET", "RENDER", "TAO"],
    "🐸 Meme": ["PEPE", "DOGE", "BONK"],
    "⛓️ Layer1": ["SOL", "SUI", "APT"]
}
```

*   **实时生效**: 修改此文件后，无需重启程序（定时任务模式下），下一次分析会自动应用。
*   **智能补全**: 如果您没填，系统也会尝试用 AI 自动判断，但手动配置更准确。

### ⚖️ 风险等级 (risk_levels)

定义不同板块的风险属性，AI 会据此给出投资建议。

```json
"risk_levels": {
    "low": ["Layer1", "BTC"],      // 🛡️ 稳健区
    "medium": ["DeFi", "Oracle"],  // ⚖️ 平衡区
    "high": ["Meme", "AI"]         // 🎢 激进区
}
```

---

## 3. 🛠️ 代码级配置 (settings.py)

位于 `config/settings.py`。

这里包含了一些路径计算和日志轮转策略。除非您是开发者并需要修改项目结构，否则**建议保持默认**。

*   **日志路径**: 默认为 `logs/okx_research.log`。
*   **日志轮转**: 单个日志最大 10MB，保留 5 个备份。

---

## 💡 常见配置案例

### 👨‍💻 本地调试模式
只想在终端看一眼现在的市场分析：
```ini
LLM_API_KEY=sk-xxxxxx
ENABLE_SCHEDULER=false
```

### 🤖 24小时无人值守模式
部署在服务器，每小时推送到飞书群：
```ini
LLM_API_KEY=sk-xxxxxx
ENABLE_SCHEDULER=true
SCHEDULE_INTERVAL=60
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/xxx
```
