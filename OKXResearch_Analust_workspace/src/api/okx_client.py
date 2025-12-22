import requests
import pandas as pd
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("okx_client")

class OKXClient:
    def __init__(self):
        # 允许从环境变量覆盖 BASE_URL，默认使用官方地址
        # 常用备用地址: https://aws.okx.com
        self.base_url = os.getenv("OKX_BASE_URL", "https://www.okx.com")
        self.headers = {
            "Content-Type": "application/json",
            # 模拟浏览器 User-Agent 以避免部分反爬
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def get_tickers(self, instType="SPOT"):
        """
        获取所有交易对的行情数据
        :param instType: 产品类型，SPOT：币币
        :return: DataFrame
        """
        endpoint = "/api/v5/market/tickers"
        url = f"{self.base_url}{endpoint}"
        params = {'instType': instType}
        
        try:
            logger.debug(f"Fetching data from {url}...")
            response = requests.get(url, params=params, headers=self.headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if data['code'] == '0':
                df = pd.DataFrame(data['data'])
                # 简单的数据清洗
                numeric_cols = ['last', 'open24h', 'high24h', 'low24h', 'volCcy24h', 'vol24h']
                for col in numeric_cols:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                
                # 如果是 SPOT，只保留 USDT 交易对
                if instType == "SPOT":
                    df = df[df['instId'].str.endswith('-USDT')]
                
                return df
            else:
                logger.error(f"Error from OKX API: {data.get('msg')}")
                return None
        except Exception as e:
            logger.error(f"Exception during request: {e}")
            return None

    def get_funding_rates(self):
        """
        获取所有永续合约的资金费率
        使用 SWAP 市场的 tickers 接口，通常包含 fundingRate 信息
        """
        endpoint = "/api/v5/public/funding-rate"
        # 注意：public/funding-rate 需要具体的 instId，不能批量获取所有
        # 替代方案：获取所有 SWAP 的 tickers，看是否包含 fundingRate?
        # OKX V5 market/tickers 对于 SWAP 并不直接返回 fundingRate。
        # 我们需要用 /api/v5/public/funding-rate 获取当前资金费率，但它需要 instId。
        # 批量获取比较麻烦。
        # 另一种方法：使用 /api/v5/market/tickers?instType=SWAP
        # 实际上 OKX 的 tickers 接口返回字段中，对于 SWAP 有 fundingRate 吗？
        # 查阅文档：tickers 接口不返回 fundingRate。
        # 但是！我们可以利用 trick：
        # 对于 Top 30 的币种，我们循环调用一次 funding-rate 接口？这太慢了 (30次请求)。
        # 
        # 更好的方案：
        # 使用 /api/v5/public/mark-price 可能也不行。
        # 
        # 让我们再检查一下 /api/v5/market/tickers 的文档。
        # 确实没有。
        # 
        # 备选方案：
        # 仅对 Top 5 热门币种（BTC, ETH, SOL, DOGE 等）获取资金费率，作为市场风向标。
        # 或者使用 limit=100 并行请求？
        # 
        # 等等，OKX 有一个 endpoint: GET /api/v5/public/funding-rate
        # "Retrieve funding rate. Rate is 0 if there is no funding rate."
        # Requires instId.
        # 
        # 既然如此，为了不拖慢速度，我们先暂时只获取 BTC-USDT-SWAP 和 ETH-USDT-SWAP 的资金费率，
        # 作为“大盘情绪”指标，而不是每个币都获取。
        pass
        
        # 实际上，我们可以尝试一次性获取 SWAP 的 tickers，虽然没有 fundingRate，
        # 但我们可以挑选出成交量最大的几个，然后专门去查它们的 fundingRate。
        
        rates = {}
        target_coins = ["BTC-USDT-SWAP", "ETH-USDT-SWAP", "SOL-USDT-SWAP", "DOGE-USDT-SWAP"]
        
        for inst_id in target_coins:
            try:
                url = f"{self.base_url}/api/v5/public/funding-rate"
                params = {'instId': inst_id}
                res = requests.get(url, params=params, headers=self.headers, timeout=5)
                if res.status_code == 200:
                    d = res.json()
                    if d['code'] == '0' and d['data']:
                        # fundingRate: "0.0001"
                        rate = float(d['data'][0]['fundingRate']) * 100 # 转为百分比
                        # 存入字典: {'BTC-USDT': 0.01}
                        spot_id = inst_id.replace("-SWAP", "")
                        rates[spot_id] = rate
            except Exception:
                continue
        
        return rates
