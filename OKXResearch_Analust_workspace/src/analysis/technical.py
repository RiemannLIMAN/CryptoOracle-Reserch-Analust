import pandas as pd

def calculate_change(current, open_price):
    """计算涨跌幅"""
    if open_price == 0:
        return 0.0
    return ((current - open_price) / open_price) * 100

def calculate_volatility(df, window=24):
    """
    计算波动率 (简单示例：使用高低价差)
    实际应用中可能需要更复杂的历史数据
    """
    if 'high24h' in df.columns and 'low24h' in df.columns:
        high = pd.to_numeric(df['high24h'], errors='coerce')
        low = pd.to_numeric(df['low24h'], errors='coerce')
        return ((high - low) / low) * 100
    return None
