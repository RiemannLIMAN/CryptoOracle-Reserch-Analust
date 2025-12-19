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

    def analyze_market(self, market_data_summary, user_query=""):
        """
        利用 LLM 分析市场数据
        :param market_data_summary: 市场数据的摘要字符串
        :param user_query: 用户特定的查询需求
        """
        if not self.api_key:
            return "Error: LLM API Key is missing. Please configure .env file."

        system_prompt = """你是一个专业的加密货币市场分析师。你的分析风格需要兼备专业深度与通俗易懂性，即便是新手也能理解复杂的市场动态。你的任务是根据提供的市场数据，分析币种的区别，并给出投资建议。

请严格遵守以下输出格式要求，不要包含任何寒暄语（如“你好”、“作为分析师...”）：

1. **核心市场摘要**：用简练且通俗的语言总结当前市场整体情绪（100字以内）。
2. **重点币种分析表格**：必须使用 Markdown 表格形式，列头包含：币种、赛道、24h涨跌幅、分析与评价（简短且易懂）。选取3-5个最具代表性的币种。
3. **赛道机会与风险**：
   - 🟢 **机会**：列出1-2个潜力赛道或币种，并说明理由（逻辑清晰，通俗易懂）。
   - 🔴 **风险**：列出需回避的板块或币种。
4. **投资建议**：针对稳健型和激进型投资者的具体操作建议，建议需具体且易于执行。

保持客观、理性，数据驱动。语言风格需专业严谨但通俗易懂，避免过度堆砌术语，对关键概念可做简要解释。使用 Markdown 格式优化排版。
"""
        
        user_prompt = f"""
以下是当前 OKX 市场的部分热门币种数据摘要（已按交易量排序）：
{market_data_summary}

用户的需求是：{user_query if user_query else "分析这些币种的区别，并推荐值得关注的币种。"}

请给出详细的分析报告。
"""

        return self._call_llm(system_prompt, user_prompt)

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
