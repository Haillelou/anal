import pandas as pd
import numpy as np
import akshare as ak
from datetime import datetime, timedelta
from risk_management.risk_calculator import RiskCalculator
from utils.stock_selector import StockSelector

class HotThemeStrategy:
    def __init__(self, initial_capital=1000000):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.positions = {}  # 当前持仓
        self.risk_calculator = RiskCalculator()
        self.stock_selector = StockSelector()
        self.max_position_count = 5  # 最大持仓数量
        self.position_size = 0.2  # 单个股票仓位比例
        
    def run_daily_strategy(self):
        """执行每日交易策略"""
        # 1. 获取当日热点题材股票
        hot_stocks = self.stock_selector.get_hot_theme_stocks()
        
        # 2. 选择最具潜力的4-5支股票
        selected_stocks = self.stock_selector.filter_best_stocks(hot_stocks, 
                                                               max_count=self.max_position_count)
        
        # 3. 执行买入操作
        self._execute_buy_orders(selected_stocks)
        
        # 4. 检查现有持仓风险并决定是否卖出
        self._check_positions_risk()
        
    def _execute_buy_orders(self, selected_stocks):
        """执行买入操作"""
        available_positions = self.max_position_count - len(self.positions)
        if available_positions <= 0:
            return
            
        for stock in selected_stocks[:available_positions]:
            if stock['code'] not in self.positions:
                position_amount = self.current_capital * self.position_size
                self.positions[stock['code']] = {
                    'amount': position_amount,
                    'price': stock['price'],
                    'quantity': position_amount / stock['price'],
                    'entry_date': datetime.now()
                }
                
    def _check_positions_risk(self):
        """检查持仓风险并执行卖出决策"""
        for code, position in list(self.positions.items()):
            risk_score = self.risk_calculator.calculate_risk_score(code)
            
            # 根据风险分数决定卖出比例
            if risk_score >= 0.8:  # 高风险，全部卖出
                self._sell_position(code, 1.0)
            elif risk_score >= 0.6:  # 中高风险，卖出70%
                self._sell_position(code, 0.7)
            elif risk_score >= 0.4:  # 中等风险，卖出30%
                self._sell_position(code, 0.3)
                
    def _sell_position(self, code, sell_ratio):
        """执行卖出操作"""
        if code in self.positions:
            position = self.positions[code]
            sell_quantity = position['quantity'] * sell_ratio
            current_price = self.stock_selector.get_current_price(code)
            
            # 更新持仓信息
            position['quantity'] -= sell_quantity
            self.current_capital += sell_quantity * current_price
            
            # 如果全部卖出，则删除持仓记录
            if sell_ratio == 1.0 or position['quantity'] < 1:
                del self.positions[code]
                
    def get_strategy_status(self):
        """获取策略当前状态"""
        return {
            'current_capital': self.current_capital,
            'position_count': len(self.positions),
            'positions': self.positions
        } 