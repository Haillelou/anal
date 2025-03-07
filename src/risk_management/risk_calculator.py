import numpy as np
import pandas as pd
import akshare as ak
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timedelta

class RiskCalculator:
    def __init__(self):
        self.scaler = MinMaxScaler()
        self.risk_threshold = 0.7
        self.volume_weight = 0.3
        self.price_change_weight = 0.3
        self.volatility_weight = 0.4
        self.risk_history = []
        self.risk_dates = []
        
    def calculate_risk_score(self, stock_code):
        """计算股票风险分数"""
        try:
            # 获取股票最近的交易数据
            stock_data = self._get_stock_data(stock_code)
            
            # 计算各个风险指标
            volume_risk = self._calculate_volume_risk(stock_data)
            price_change_risk = self._calculate_price_change_risk(stock_data)
            volatility_risk = self._calculate_volatility_risk(stock_data)
            
            # 综合风险评分
            risk_score = (volume_risk * self.volume_weight +
                         price_change_risk * self.price_change_weight +
                         volatility_risk * self.volatility_weight)
            
            # 记录风险分数
            self._record_risk_score(risk_score)
            
            return min(max(risk_score, 0), 1)  # 确保风险分数在0-1之间
            
        except Exception as e:
            print(f"计算风险分数时出错: {e}")
            return 1.0  # 出错时返回最高风险分数
            
    def _record_risk_score(self, risk_score):
        """记录风险分数历史"""
        self.risk_history.append(risk_score)
        self.risk_dates.append(datetime.now())
        
        # 只保留最近30天的数据
        if len(self.risk_history) > 30:
            self.risk_history = self.risk_history[-30:]
            self.risk_dates = self.risk_dates[-30:]
            
    def get_recent_dates(self):
        """获取最近的日期列表"""
        return self.risk_dates
        
    def get_recent_risk_scores(self):
        """获取最近的风险分数列表"""
        return self.risk_history
        
    def _get_stock_data(self, stock_code):
        """获取股票数据"""
        # 使用akshare获取股票数据
        stock_data = ak.stock_zh_a_hist(symbol=stock_code, period="daily", 
                                      start_date=self._get_start_date(), 
                                      end_date=self._get_end_date())
        return stock_data
        
    def _calculate_volume_risk(self, stock_data):
        """计算成交量风险
        成交量突然放大通常意味着风险增加
        """
        volumes = stock_data['成交量'].values
        if len(volumes) < 2:
            return 1.0
            
        # 计算成交量变化率
        volume_change = (volumes[-1] - np.mean(volumes[:-1])) / np.mean(volumes[:-1])
        normalized_volume_risk = self.scaler.fit_transform([[abs(volume_change)]])[0][0]
        return normalized_volume_risk
        
    def _calculate_price_change_risk(self, stock_data):
        """计算价格变化风险
        价格快速上涨通常意味着回调风险增加
        """
        prices = stock_data['收盘'].values
        if len(prices) < 2:
            return 1.0
            
        # 计算价格变化率
        price_change = (prices[-1] - prices[0]) / prices[0]
        normalized_price_risk = self.scaler.fit_transform([[abs(price_change)]])[0][0]
        return normalized_price_risk
        
    def _calculate_volatility_risk(self, stock_data):
        """计算波动率风险
        波动率越大，风险越高
        """
        prices = stock_data['收盘'].values
        if len(prices) < 2:
            return 1.0
            
        # 计算日收益率的标准差
        returns = np.diff(np.log(prices))
        volatility = np.std(returns)
        normalized_volatility_risk = self.scaler.fit_transform([[volatility]])[0][0]
        return normalized_volatility_risk
        
    def _get_start_date(self):
        """获取开始日期（5个交易日前）"""
        return (pd.Timestamp.now() - pd.Timedelta(days=7)).strftime('%Y%m%d')
        
    def _get_end_date(self):
        """获取结束日期（今天）"""
        return pd.Timestamp.now().strftime('%Y%m%d') 