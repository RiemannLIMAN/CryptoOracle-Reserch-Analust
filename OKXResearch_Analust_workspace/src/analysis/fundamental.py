import json
from pathlib import Path
from api.llm_client import LLMClient
import logging

logger = logging.getLogger("fundamental")

class FundamentalAnalyzer:
    def __init__(self, config_path=None):
        if config_path:
            self.config_path = Path(config_path)
        else:
            # 默认尝试从 config 目录加载
            self.config_path = Path(__file__).resolve().parent.parent.parent / "config" / "coins_data.json"
        
        self.local_sector_map = self._load_local_sector_data()
        self.llm_client = LLMClient()
        self.memory_cache = {} # 内存缓存，避免重复请求 LLM

    def _load_local_sector_data(self):
        """加载本地币种赛道数据作为兜底"""
        if not self.config_path.exists():
            return {}
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                coin_map = {}
                for sector, coins in data.get('sectors', {}).items():
                    for coin in coins:
                        coin_map[coin] = sector
                return coin_map
        except Exception as e:
            logger.error(f"Error loading local fundamental data: {e}")
            return {}

    def get_coin_sector(self, coin_symbol):
        """
        获取币种所属赛道
        优先级: 内存缓存 -> 本地配置 -> LLM 实时查询 -> Unknown
        """
        # 移除 -USDT 后缀
        base_symbol = coin_symbol.split('-')[0]
        
        # 1. 查内存缓存
        if base_symbol in self.memory_cache:
            return self.memory_cache[base_symbol]

        # 2. 查本地配置 (coins_data.json)
        if base_symbol in self.local_sector_map:
            return self.local_sector_map[base_symbol]

        # 3. 如果本地也没有，且没有配置 LLM，直接返回 Unknown，避免阻塞
        if not self.llm_client.api_key:
             return "Unknown"

        # 注意：这里如果每个币都单独调 LLM 会太慢。
        # 实际生产中建议批量查询。为了简化逻辑，这里暂时返回 Unknown，
        # 而是提供一个 batch_update_sectors 方法供外部调用。
        return "Unknown"

    def update_sectors_with_ai(self, coin_list):
        """
        批量使用 AI 更新赛道信息
        """
        # 找出所有未知的币种
        unknown_coins = []
        for coin in coin_list:
            base = coin.split('-')[0]
            if self.get_coin_sector(coin) == "Unknown":
                unknown_coins.append(base)
        
        if not unknown_coins:
            return

        logger.info(f"Identifying sectors for {len(unknown_coins)} new coins using AI...")
        
        # 每次最多处理 20 个，避免 token 溢出
        chunk_size = 20
        for i in range(0, len(unknown_coins), chunk_size):
            batch = unknown_coins[i:i+chunk_size]
            try:
                ai_result = self.llm_client.classify_sectors(batch)
                if ai_result:
                    self.memory_cache.update(ai_result)
                    logger.info(f"AI identified {len(ai_result)} sectors.")
            except Exception as e:
                logger.error(f"Failed to identify sectors with AI: {e}")
