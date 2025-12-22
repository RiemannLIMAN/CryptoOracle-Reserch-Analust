import json
import os
import datetime
import logging
from pathlib import Path

logger = logging.getLogger("paper_trader")

class PaperTrader:
    def __init__(self, data_dir="data", initial_balance=10000.0):
        self.data_file = Path(data_dir) / "paper_trading.json"
        self.initial_balance = initial_balance
        self.portfolio = self._load_portfolio()

    def _load_portfolio(self):
        """加载或初始化投资组合数据"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load paper trading data: {e}")
        
        # 初始化默认数据
        return {
            "balance": self.initial_balance,  # USDT 余额
            "positions": {},       # 持仓: {"BTC-USDT": 0.1, ...}
            "total_value": self.initial_balance, # 总资产市值
            "history": [],         # 交易历史
            "last_updated": None
        }

    def _save_portfolio(self):
        """保存数据到磁盘"""
        try:
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.portfolio, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save paper trading data: {e}")

    def execute_trade(self, action, symbol, price, amount_usdt, reason=""):
        """
        执行模拟交易
        :param action: "buy" or "sell"
        :param symbol: 交易对 (e.g., "BTC-USDT")
        :param price: 当前价格
        :param amount_usdt: 交易金额 (USDT)
        :param reason: 交易理由
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if action == "buy":
            cost = amount_usdt
            if self.portfolio["balance"] < cost:
                logger.warning(f"Insufficient balance to buy {symbol}. Need: {cost}, Have: {self.portfolio['balance']}")
                return False
            
            # 扣款
            self.portfolio["balance"] -= cost
            # 加仓 (数量 = 金额 / 价格)
            quantity = cost / price
            current_qty = self.portfolio["positions"].get(symbol, 0.0)
            self.portfolio["positions"][symbol] = current_qty + quantity
            
            log_msg = f"BUY {symbol}: {cost} USDT @ {price} (Qty: {quantity:.6f})"
            
        elif action == "sell":
            # 卖出逻辑：amount_usdt 这里理解为“卖出多少钱的货”，或者全部卖出
            # 简化逻辑：如果 amount_usdt = -1，则清仓
            
            current_qty = self.portfolio["positions"].get(symbol, 0.0)
            if current_qty <= 0:
                logger.warning(f"No position to sell for {symbol}")
                return False
            
            if amount_usdt == -1 or amount_usdt >= current_qty * price:
                # 清仓
                sell_qty = current_qty
                revenue = sell_qty * price
                del self.portfolio["positions"][symbol]
                log_msg = f"SELL ALL {symbol}: {revenue:.2f} USDT @ {price}"
            else:
                # 减仓
                sell_qty = amount_usdt / price
                revenue = amount_usdt
                self.portfolio["positions"][symbol] -= sell_qty
                log_msg = f"SELL {symbol}: {revenue:.2f} USDT @ {price}"
            
            # 入账
            self.portfolio["balance"] += revenue
            
        else:
            return False

        # 记录历史
        record = {
            "time": timestamp,
            "action": action,
            "symbol": symbol,
            "price": price,
            "amount_usdt": amount_usdt,
            "reason": reason
        }
        self.portfolio["history"].append(record)
        self.portfolio["last_updated"] = timestamp
        
        logger.info(f"Paper Trade Executed: {log_msg}. Reason: {reason}")
        self._save_portfolio()
        return True

    def update_valuations(self, current_prices):
        """
        更新账户总市值
        :param current_prices: 字典 {symbol: price}
        """
        position_value = 0.0
        for symbol, qty in self.portfolio["positions"].items():
            price = current_prices.get(symbol, 0.0)
            if price > 0:
                position_value += qty * price
        
        self.portfolio["total_value"] = self.portfolio["balance"] + position_value
        self._save_portfolio()
        
        return self.portfolio["total_value"]

    def get_report(self):
        """生成简单的持仓报告"""
        pnl_pct = (self.portfolio["total_value"] - self.initial_balance) / self.initial_balance * 100
        
        report = f"💰 **模拟盘周报**\n"
        report += f"总资产: {self.portfolio['total_value']:.2f} USDT (收益率: {pnl_pct:+.2f}%)\n"
        report += f"可用余额: {self.portfolio['balance']:.2f} USDT\n"
        
        if self.portfolio["positions"]:
            report += "当前持仓:\n"
            for sym, qty in self.portfolio["positions"].items():
                report += f"- {sym}: {qty:.6f}\n"
        else:
            report += "当前空仓\n"
            
        return report
