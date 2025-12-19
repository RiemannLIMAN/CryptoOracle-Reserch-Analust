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
                
                # 计算涨跌幅 (当前价格 - 开盘价格) / 开盘价格
                # OKX 接口其实可能有返回涨跌幅，但我们也可以自己算以确保
                # 这里主要关注 USDT 交易对，过滤掉其他的
                df = df[df['instId'].str.endswith('-USDT')]
                
                return df
            else:
                logger.error(f"Error from OKX API: {data.get('msg')}")
                return None
        except Exception as e:
            logger.error(f"Exception during request: {e}")
            return None
