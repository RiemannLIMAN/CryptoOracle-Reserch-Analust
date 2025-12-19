import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 基础路径
BASE_DIR = Path(__file__).resolve().parent.parent

# OKX 配置
OKX_API_KEY = os.getenv("OKX_API_KEY")
OKX_SECRET_KEY = os.getenv("OKX_SECRET_KEY")
OKX_PASSPHRASE = os.getenv("OKX_PASSPHRASE")
OKX_BASE_URL = os.getenv("OKX_BASE_URL", "https://www.okx.com")

# LLM (大模型) 配置
# 优先读取 LLM_ 前缀的配置，如果未设置则尝试读取 DEEPSEEK_ 前缀以保持兼容性
LLM_API_KEY = os.getenv("LLM_API_KEY") or os.getenv("DEEPSEEK_API_KEY")
LLM_BASE_URL = os.getenv("LLM_BASE_URL") or os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-chat")

# 调度与通知配置
ENABLE_SCHEDULER = os.getenv("ENABLE_SCHEDULER", "false").lower() == "true"
SCHEDULE_TIME = os.getenv("SCHEDULE_TIME", "08:00") # 默认每天早上8点
SCHEDULE_INTERVAL = int(os.getenv("SCHEDULE_INTERVAL", "0")) # 默认0，表示不启用间隔模式
FEISHU_WEBHOOK_URL = os.getenv("FEISHU_WEBHOOK_URL")
DINGTALK_WEBHOOK_URL = os.getenv("DINGTALK_WEBHOOK_URL")

# 日志配置
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
