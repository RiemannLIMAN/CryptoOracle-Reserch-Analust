import os
import requests
import json
import logging
from config.settings import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL

logger = logging.getLogger("llm_client")

class LLMClient:
    def __init__(self):
        self.api_key = LLM_API_KEY
        self.base_url = LLM_BASE_URL
        self.model = LLM_MODEL
        
        # 兼容性处理：如果用户只配置了 base_url (如 https://api.deepseek.com) 
        # 但没有包含具体的 chat 路径，我们尝试自动补充标准 OpenAI 格式路径
        if self.base_url and not self.base_url.endswith("/chat/completions"):
            # 如果结尾是 /v1，则补全 /chat/completions
            if self.base_url.endswith("/v1"):
                self.base_url = f"{self.base_url}/chat/completions"
            # 否则假设这是一个根域名，尝试补充 /chat/completions 或 /v1/chat/completions
            # 这里为了通用性，默认假设用户填写的是 base_url (e.g. https://api.openai.com/v1)
            # 如果用户填写的已经是完整路径，则不改动
            else:
                self.base_url = f"{self.base_url.rstrip('/')}/chat/completions"

        if not self.api_key:
            logger.warning("Notice: LLM_API_KEY not found. AI analysis will not be available.")
        else:
            logger.debug(f"LLM Client initialized with model: {self.model}")

    def verify_and_analyze_news(self, news_items):
        """
        验证新闻真实性并分析情感
        :param news_items: 新闻列表（字典列表，包含 title, source, domain 等）
        """
        if not self.api_key or not news_items:
            return None

        # 格式化新闻输入
        news_str = ""
        for idx, item in enumerate(news_items[:5]): # 每次只分析前5条，避免token超限
            news_str += f"{idx+1}. [{item.get('domain', 'Unknown')}] {item['title']} (发布时间: {item.get('published_at', 'Unknown')})\n"

        system_prompt = """你是一个专业的加密货币情报分析师。请对以下新闻进行【简短而精准】的逻辑推演。
不要复述新闻内容，而是直接指出：这条新闻背后的逻辑是什么？会导致什么结果？

请输出 JSON 格式（不要 Markdown）：
{
    "market_summary": "一句话总结当前最核心的市场叙事（50字以内）。",
    "verified_news": [
        {
            "id": 1,
            "title": "简化的新闻标题（不要超过20字）",
            "credibility": "High" | "Medium" | "Low",
            "impact": "High" | "Medium",
            "logic": "简短的一句话逻辑推演（例如：MicroStrategy 再次买入 BTC -> 减少市场流通量 -> 长期利好）",
            "sentiment_score": 0.8
        }
    ]
}
"""
        
        user_prompt = f"""
以下是来自聚合器的最新加密新闻：
{news_str}

请进行验证和逻辑推演：
"""
        try:
            response = self._call_llm(system_prompt, user_prompt)
            # 清理 Markdown
            clean_json = response.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)
        except Exception as e:
            logger.error(f"News verification failed: {e}")
            return None

    def analyze_market(self, market_data_summary, user_query="", news_analysis=None):
        """
        利用 LLM 分析市场数据 (结合新闻)
        :param market_data_summary: 市场数据的摘要字符串
        :param user_query: 用户特定的查询需求
        :param news_analysis: 验证过的新闻情报 (JSON dict)
        """
        if not self.api_key:
            return "Error: LLM API Key is missing. Please configure .env file."

        # 构建新闻摘要文本
        news_context = ""
        if news_analysis and news_analysis.get('verified_news'):
            # 将新闻整合为一个独立板块，只列出核心逻辑
            news_context = "\n\n📰 **新闻情报与逻辑推演**:\n"
            news_context += f"> **当前叙事**: {news_analysis.get('market_summary', '无')}\n\n"
            
            # 使用表格形式展示新闻，更清晰
            news_context += "| 信号 | 新闻标题 | 逻辑与影响 |\n"
            news_context += "| :---: | :--- | :--- |\n"
            
            for news in news_analysis['verified_news']:
                # 只展示高/中可信度且非噪音的新闻
                if news['credibility'] != 'Low' and news.get('impact') != 'Low':
                    sentiment_icon = "🟢" if news['sentiment_score'] > 0 else "🔴"
                    
                    # 清理换行符，防止破坏表格
                    title = news.get('title', 'Unknown').replace('\n', ' ').replace('|', '/')
                    logic = news.get('logic', '无逻辑推演').replace('\n', ' ').replace('|', '/')
                    
                    # 截断过长的标题
                    if len(title) > 50:
                        title = title[:50] + "..."
                    
                    news_context += f"| {sentiment_icon} | {title} | {logic} |\n"

        system_prompt = """你是一个专业的加密货币市场分析师。你的分析风格需要兼备专业深度与通俗易懂性。

核心任务：
1. **结合新闻逻辑与盘面数据**：不要割裂地看新闻和K线。如果新闻利好但价格下跌，请指出这种背离。
2. **简短准确**：在分析中，用一句话点破新闻带来的逻辑影响。

请严格遵守以下输出格式要求，不要包含任何寒暄语：

1. **核心市场摘要**：总结当前市场整体情绪，必须结合新闻面和技术面。
2. **📰 新闻情报区**：
   - 直接展示上方提供的【新闻情报与逻辑推演】表格内容。
   - **重要**：如果上方提供了表格，请原封不动地将其复制到这里，保持 Markdown 表格格式，不要将其转换为文本列表。
3. **重点币种分析表格**：Markdown 表格，列头：币种、赛道、24h涨跌幅、分析与评价。
4. **赛道机会与风险**：
   - 🟢 **机会**：列出潜力赛道或币种。
   - 🔴 **风险**：列出需回避的板块或币种。
5. **投资建议**：针对稳健型和激进型投资者的具体操作建议。

关于资金费率 (Funding Rate) 的说明：
- 正值 (>0)：代表多头支付空头费用，数值越高（如 >0.03%），表明做多情绪越拥挤。
- 负值 (<0)：代表空头支付多头费用，数值越低，表明做空情绪越浓。

保持客观、理性，数据驱动。语言风格需专业严谨但通俗易懂。
"""
        
        user_prompt = f"""
以下是当前 OKX 市场的部分热门币种数据摘要（已按交易量排序）：
{market_data_summary}

{news_context}

用户的需求是：{user_query if user_query else "分析这些币种的区别，并推荐值得关注的币种。"}

请给出详细的分析报告。
"""

        return self._call_llm(system_prompt, user_prompt)

    def get_trade_decision(self, market_analysis, current_portfolio):
        """
        基于市场分析报告和当前持仓，生成模拟交易指令
        :param market_analysis: 刚才生成的分析报告
        :param current_portfolio: 当前持仓状态 (字符串描述)
        """
        if not self.api_key:
            return None

        system_prompt = """你是一个专业的量化交易员。你的任务是根据市场分析报告和当前持仓，给出一个明确的模拟交易指令。
你的初始资金是 10000 USDT。
请仅返回一个 JSON 对象，不要包含任何 Markdown 标记或解释文字。

JSON 格式要求：
{
    "action": "buy" | "sell" | "hold",
    "symbol": "BTC-USDT",  # 必须是分析报告中提到的币种
    "amount_usdt": 1000,   # 买入金额（USDT），或者卖出金额（-1 代表清仓）
    "reason": "简短的交易理由（20字以内）"
}

规则：
1. 如果市场不明朗或风险较高，请选择 "hold"（观望）。
2. 单次交易金额建议控制在总资金的 10%-20% 以内（约 1000-2000 U），做好风控。
3. 如果决定买入，确保理由充分（如：资金费率异常、突破关键位、板块轮动）。
4. 如果当前持有某币种且分析提示风险，可考虑 "sell"。
"""
        
        user_prompt = f"""
[市场分析报告]
{market_analysis}

[当前持仓状态]
{current_portfolio}

请给出你的交易决策（JSON格式）：
"""
        try:
            response = self._call_llm(system_prompt, user_prompt)
            # 清理 Markdown
            clean_json = response.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)
        except Exception as e:
            logger.error(f"Failed to generate trade decision: {e}")
            return None


    def classify_sectors(self, coin_list):
        """
        利用 LLM 对币种进行赛道分类
        :param coin_list: 币种列表 (list of strings)
        :return: 字典 {coin: sector}
        """
        if not self.api_key:
            return {}

        coins_str = ", ".join(coin_list)
        system_prompt = """你是一个加密货币领域的专家百科全书。你的任务是识别给定币种所属的主流赛道（Sector）。
只返回纯 JSON 格式数据，不要包含 Markdown 标记或其他文字。
格式要求：{"BTC": "Layer1", "UNI": "DeFi", ...}
赛道分类参考：Layer1, Layer2, DeFi, Meme, AI, GameFi, RWA, Storage, Oracle 等。如果不知道，标记为 "Unknown"。
"""
        user_prompt = f"请对以下币种进行分类：{coins_str}"
        
        try:
            response_text = self._call_llm(system_prompt, user_prompt)
            # 清理可能的 markdown 标记
            response_text = response_text.replace("```json", "").replace("```", "").strip()
            return json.loads(response_text)
        except Exception as e:
            logger.error(f"Error classifying sectors: {e}")
            return {}

    def _call_llm(self, system_prompt, user_prompt):
        """通用 LLM 调用方法"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "stream": False
        }

        try:
            # logger.info(f"Sending request to LLM ({self.model})...") 
            # 避免日志过于嘈杂，仅在 debug 级别或外部调用时记录
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']
            else:
                logger.error(f"Unexpected response structure: {result}")
                raise ValueError("Unexpected response from LLM API")
                
        except Exception as e:
            logger.error(f"Error calling LLM API: {e}")
            raise
