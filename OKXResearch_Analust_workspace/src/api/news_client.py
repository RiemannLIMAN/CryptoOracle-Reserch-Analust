import requests
import logging
import os
try:
    from config.settings import CRYPTOPANIC_API_KEY
except ImportError:
    CRYPTOPANIC_API_KEY = os.getenv("CRYPTOPANIC_API_KEY")

logger = logging.getLogger("news_client")

class NewsClient:
    def __init__(self):
        self.api_key = CRYPTOPANIC_API_KEY
        self.base_url = "https://cryptopanic.com/api/v1/posts/"
        
        if not self.api_key:
            logger.warning("CryptoPanic API Key not found. News features will be disabled.")

    def get_latest_news(self, filter="hot", currencies=None, limit=10):
        """
        获取最新加密货币新闻
        :param filter: "hot" (热门), "rising" (飙升), "bullish" (利多), "bearish" (利空)
        :param currencies: 币种代码列表，如 ["BTC", "ETH"]
        :param limit: 获取条数限制
        :return: 新闻列表 (list of dict)
        """
        if not self.api_key:
            return []

        # 策略：如果不指定 currencies，我们先尝试获取全局热门新闻
        # 如果指定了，就按指定获取。
        # 这里为了确保获取到“有价值”的新闻，我们可以尝试混合策略？
        # 目前 CryptoPanic 的 filter="hot" 已经是基于热度算法了，通常就是最重要的。
        # 
        # 但为了提高信噪比，我们可以增加 filter="important" (如果API支持)
        # 查阅 CryptoPanic 文档，filter 只有 rising, hot, bullish, bearish, important, saved, lol.
        # 所以我们可以改用 filter="important" 或者是 "hot"
        
        params = {
            "auth_token": self.api_key,
            "filter": "important", # 改为 important，只看重要新闻
            "public": "true",
            "kind": "news" # 只看新闻，过滤掉纯媒体内容
        }
        
        if currencies:
            params["currencies"] = ",".join(currencies)

        try:
            logger.info(f"Fetching news from CryptoPanic (filter={params['filter']})...")
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = data.get('results', [])
            
            # 如果 important 没数据，降级为 hot
            if not results and params['filter'] == 'important':
                logger.info("No important news found, falling back to hot news...")
                params['filter'] = 'hot'
                response = requests.get(self.base_url, params=params, timeout=10)
                data = response.json()
                results = data.get('results', [])

            # 简单的预处理
            processed_news = []
            for item in results[:limit]:
                # 增加 source 信息，辅助 AI 判断价值
                source_title = item.get("source", {}).get("title", "Unknown")
                
                news_item = {
                    "id": item.get("id"),
                    "title": item.get("title"),
                    "domain": item.get("domain"),
                    "source": source_title, # 新增来源
                    "votes": item.get("votes", {}), # 新增投票数据 (bullish/bearish/important)
                    "published_at": item.get("published_at"),
                    "url": item.get("url"),
                    "currencies": [c['code'] for c in item.get("currencies", []) if 'code' in c]
                }
                processed_news.append(news_item)
                
            return processed_news
            
        except Exception as e:
            logger.error(f"Failed to fetch news: {e}")
            return []
