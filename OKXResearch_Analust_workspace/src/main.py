import sys
import os
import pandas as pd

# 将 src 目录和项目根目录添加到 Python 路径
src_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(src_path)
sys.path.append(src_path)
sys.path.append(project_root)

from api.okx_client import OKXClient
from api.llm_client import LLMClient
from analysis.fundamental import FundamentalAnalyzer
from analysis.technical import calculate_change
from api.news_client import NewsClient
from utils.logger import setup_logger
from utils.notifier import Notifier
from config.settings import LOG_DIR, ENABLE_SCHEDULER, SCHEDULE_TIME, SCHEDULE_INTERVAL, FEISHU_WEBHOOK_URL, DINGTALK_WEBHOOK_URL
# 从根目录的 __init__.py 导入版本信息
from src import __version__, __author__
import datetime
import logging
import schedule
import time
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

# 配置固定日志文件名，以便 RotatingFileHandler 生效
log_file = LOG_DIR / "okx_research.log"

# 配置 root logger，使其输出到文件和控制台
# 注意：这里我们使用 name=None 来配置 root logger
setup_logger(name=None, log_file=log_file)

# 获取 main 模块的 logger
logger = logging.getLogger("main")

# 初始化 Rich Console
console = Console()

def print_welcome():
    """打印启动欢迎信息"""
    # 记录到日志文件
    logger.info(f"System Startup - Version: {__version__}, Author: {__author__}")
    
    # 打印到终端 UI
    console.print(Panel(
        f"[bold green]OKX Research Analyst[/bold green]\n"
        f"Version: [yellow]{__version__}[/yellow]\n"
        f"Author: [blue]{__author__}[/blue]\n"
        f"Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        title="🚀 System Startup",
        border_style="green"
    ))

def format_data_for_llm(df, analyzer, funding_rates=None, top_n=20):
    """
    将 DataFrame 格式化为 LLM 易读的字符串，并补充赛道信息
    """
    if funding_rates is None:
        funding_rates = {}

    # 确保 volCcy24h 是数值类型
    df['volCcy24h'] = pd.to_numeric(df['volCcy24h'], errors='coerce')
    
    # 按成交额排序
    df_sorted = df.sort_values(by='volCcy24h', ascending=False).head(top_n)
    
    summary = []
    for _, row in df_sorted.iterrows():
        try:
            last_price = float(row['last'])
            open_price = float(row['open24h'])
            vol = float(row['volCcy24h'])
            
            # 使用 technical 模块计算涨跌幅
            change_pct = calculate_change(last_price, open_price)
            
            # 获取赛道信息
            inst_id = row['instId']
            # 使用传入的 analyzer 实例，利用其缓存
            sector = analyzer.get_coin_sector(inst_id)
            
            line = (f"Symbol: {inst_id}, "
                    f"Price: {last_price}, "
                    f"Sector: {sector}, "
                    f"24h Change: {change_pct:.2f}%, "
                    f"24h Vol(USDT): {vol:.0f}")
            
            # 补充资金费率 (如果有)
            # inst_id 如 BTC-USDT，funding_rates 键也是 BTC-USDT
            if inst_id in funding_rates:
                fr = funding_rates[inst_id]
                line += f", Funding Rate: {fr:.4f}%"
            
            summary.append(line)
        except ValueError:
            continue
            
    return "\n".join(summary)

def run_analysis_task(user_query=""):
    """
    执行一次完整的分析任务：抓取 -> 预处理 -> 分析 -> 展示/通知
    """
    try:
        logger.info("Starting analysis task...")
        
        okx = OKXClient()
        llm = LLMClient()
        news = NewsClient()
        
        # 1. 获取数据
        logger.info("Fetching market data from OKX...")
        df = okx.get_tickers()
        
        # 1.1 获取资金费率 (作为大盘情绪参考)
        # 虽然这里只获取了部分主流币的费率，但对 AI 判断市场情绪很有用
        logger.info("Fetching funding rates...")
        funding_rates = okx.get_funding_rates()
        
        # 1.2 获取新闻 (新增)
        logger.info("Fetching latest crypto news...")
        # 获取热门新闻，涵盖主流币
        raw_news = news.get_latest_news(filter="hot", currencies=["BTC", "ETH", "SOL"], limit=5)
        
        # 1.3 LLM 验证新闻
        verified_news = None
        if raw_news and llm.api_key:
            logger.info("Verifying news authenticity with AI...")
            verified_news = llm.verify_and_analyze_news(raw_news)
        
        if df is None or df.empty:
            logger.error("Failed to fetch data or data is empty.")
            return

        # 2. 预处理
        logger.info(f"Fetched {len(df)} tickers. Preparing top 30 by volume for analysis...")
        
        # 提前使用 AI 批量识别这 Top 30 币种的赛道
        # 这样在 format_data_for_llm 里就能直接从缓存拿数据，不用每次都调接口
        fundamental = FundamentalAnalyzer()
        top_coins = df.sort_values(by='volCcy24h', ascending=False).head(30)['instId'].tolist()
        
        # 如果配置了 LLM，尝试自动识别未知赛道
        if llm.api_key:
            fundamental.update_sectors_with_ai(top_coins)
            
        data_summary = format_data_for_llm(df, fundamental, funding_rates=funding_rates, top_n=30)
        
        # 3. 分析
        if not llm.api_key:
             logger.warning("LLM API key not configured. Skipping analysis.")
             return
        
        logger.info(f"User Query: {user_query if user_query else 'Default Analysis'}")

        # 交互模式下显示动画，非交互模式(定时任务)则静默
        if sys.stdout.isatty():
            with console.status(f"[bold green]AI ({llm.model}) is thinking...", spinner="dots"):
                analysis = llm.analyze_market(data_summary, user_query, news_analysis=verified_news)
        else:
            logger.info(f"AI ({llm.model}) is analyzing...")
            analysis = llm.analyze_market(data_summary, user_query, news_analysis=verified_news)
            
        logger.info("Analysis completed.")

        # 4. 展示与通知
        # 终端输出
        console.print("\n")
        console.print(Panel(Markdown(analysis), title="📊 OKX Market Analysis Report", border_style="blue"))
        
        # 将完整的分析报告写入日志文件，作为存档
        logger.info(f"Analysis Report Content:\n{'-'*50}\n{analysis}\n{'-'*50}")

        # 推送通知
        if FEISHU_WEBHOOK_URL or DINGTALK_WEBHOOK_URL:
            notifier = Notifier(feishu_webhook=FEISHU_WEBHOOK_URL, dingtalk_webhook=DINGTALK_WEBHOOK_URL)
            # 截取摘要或发送完整报告（注意消息长度限制，这里发送前500字符或完整内容）
            # 实际生产中可能需要拆分发送
            notifier.send("OKX Market Analysis Report", analysis)
            
    except Exception as e:
        logger.error(f"Error occurring during analysis task: {e}", exc_info=True)
        # 在控制台也打印一下，方便调试（如果是交互模式）
        if sys.stdout.isatty():
            console.print(f"[bold red]Task Error:[/bold red] {e}")

def main():
    # 打印欢迎信息
    print_welcome()
    
    # 获取命令行参数作为用户查询
    user_query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    
    if ENABLE_SCHEDULER:
        if SCHEDULE_INTERVAL > 0:
            logger.info(f"Scheduler enabled. Task will run every {SCHEDULE_INTERVAL} minutes.")
            console.print(f"[bold green]Scheduler enabled. Running every {SCHEDULE_INTERVAL} minutes...[/bold green]")
            # 立即运行一次
            run_analysis_task(user_query)
            schedule.every(SCHEDULE_INTERVAL).minutes.do(run_analysis_task, user_query)
        else:
            logger.info(f"Scheduler enabled. Task will run daily at {SCHEDULE_TIME}.")
            console.print(f"[bold green]Scheduler enabled. Running daily at {SCHEDULE_TIME}...[/bold green]")
            # 设置定时任务
            schedule.every().day.at(SCHEDULE_TIME).do(run_analysis_task, user_query)
        
        while True:
            schedule.run_pending()
            time.sleep(60)
    else:
        # 单次运行模式
        run_analysis_task(user_query)

if __name__ == "__main__":
    main()
