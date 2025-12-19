import unittest
from src.api.okx_client import OKXClient

class TestOKXClient(unittest.TestCase):
    def setUp(self):
        self.client = OKXClient()

    def test_get_tickers(self):
        """测试能否获取到 Tickers 数据"""
        df = self.client.get_tickers()
        
        # 检查是否返回了 DataFrame
        self.assertIsNotNone(df)
        
        # 检查是否非空
        self.assertFalse(df.empty)
        
        # 检查关键列是否存在
        self.assertIn('instId', df.columns)
        self.assertIn('last', df.columns)
        
        # 检查是否只包含 USDT 交易对 (根据我们的逻辑)
        sample_instId = df.iloc[0]['instId']
        self.assertTrue(sample_instId.endswith('-USDT'))

if __name__ == '__main__':
    unittest.main()
