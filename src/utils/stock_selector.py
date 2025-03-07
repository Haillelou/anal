import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class StockSelector:
    def __init__(self):
        self.momentum_weight = 0.4
        self.volume_weight = 0.3
        self.theme_weight = 0.3
        self.stock_names_cache = {}
        
    def get_stock_name(self, stock_code):
        """获取股票名称"""
        if stock_code in self.stock_names_cache:
            return self.stock_names_cache[stock_code]
            
        try:
            stock_info = ak.stock_zh_a_spot_em()
            stock_row = stock_info[stock_info['代码'] == stock_code].iloc[0]
            name = stock_row['名称']
            self.stock_names_cache[stock_code] = name
            return name
        except:
            return stock_code
        
    def get_hot_theme_stocks(self):
        """获取热点题材股票"""
        try:
            # 获取概念板块行情
            concept_plates = ak.stock_board_concept_name_em()
            
            # 获取涨幅排名前10的概念板块
            hot_concepts = concept_plates.sort_values('涨跌幅', ascending=False).head(10)
            
            # 获取这些概念板块下的股票
            hot_stocks = []
            for _, concept in hot_concepts.iterrows():
                stocks = ak.stock_board_concept_cons_em(symbol=concept['板块代码'])
                for _, stock in stocks.iterrows():
                    hot_stocks.append({
                        'code': stock['代码'],
                        'name': stock['名称'],
                        'concept': concept['板块名称'],
                        'concept_change_pct': concept['涨跌幅']
                    })
            
            return hot_stocks
            
        except Exception as e:
            print(f"获取热点题材股票时出错: {e}")
            return []
            
    def filter_best_stocks(self, hot_stocks, max_count=5):
        """从热点股票中筛选出最具潜力的股票"""
        try:
            scored_stocks = []
            
            for stock in hot_stocks:
                # 获取股票最近的交易数据
                stock_data = self._get_stock_data(stock['code'])
                if stock_data.empty:
                    continue
                    
                # 计算动量得分
                momentum_score = self._calculate_momentum_score(stock_data)
                
                # 计算成交量得分
                volume_score = self._calculate_volume_score(stock_data)
                
                # 计算题材得分
                theme_score = self._calculate_theme_score(stock['concept_change_pct'])
                
                # 计算综合得分
                total_score = (momentum_score * self.momentum_weight +
                             volume_score * self.volume_weight +
                             theme_score * self.theme_weight)
                
                scored_stocks.append({
                    'code': stock['code'],
                    'name': stock['name'],
                    'score': total_score,
                    'price': stock_data['收盘'].iloc[-1]
                })
            
            # 按得分排序并返回前N支股票
            return sorted(scored_stocks, key=lambda x: x['score'], reverse=True)[:max_count]
            
        except Exception as e:
            print(f"筛选最佳股票时出错: {e}")
            return []
            
    def _get_stock_data(self, stock_code):
        """获取股票数据"""
        try:
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
            
            stock_data = ak.stock_zh_a_hist(symbol=stock_code, period="daily",
                                          start_date=start_date,
                                          end_date=end_date)
            return stock_data
        except:
            return pd.DataFrame()
            
    def _calculate_momentum_score(self, stock_data):
        """计算动量得分"""
        if len(stock_data) < 2:
            return 0
            
        # 计算最近的价格趋势
        prices = stock_data['收盘'].values
        returns = np.diff(np.log(prices))
        
        # 使用最近5日的平均回报率作为动量指标
        recent_momentum = np.mean(returns[-5:]) if len(returns) >= 5 else np.mean(returns)
        
        # 归一化处理
        return (recent_momentum + 0.1) / 0.2  # 假设日均波动在±10%之间
        
    def _calculate_volume_score(self, stock_data):
        """计算成交量得分"""
        if len(stock_data) < 2:
            return 0
            
        volumes = stock_data['成交量'].values
        
        # 计算最近成交量相对于过去的变化
        recent_vol = np.mean(volumes[-3:])  # 最近3日平均成交量
        past_vol = np.mean(volumes[:-3])    # 之前的平均成交量
        
        volume_change = (recent_vol - past_vol) / past_vol
        
        # 归一化处理
        return min(max((volume_change + 1) / 2, 0), 1)
        
    def _calculate_theme_score(self, concept_change_pct):
        """计算题材得分"""
        # 将涨跌幅转换为0-1之间的得分
        return min(max((concept_change_pct + 10) / 20, 0), 1)
        
    def get_current_price(self, stock_code):
        """获取当前股价"""
        try:
            stock_data = ak.stock_zh_a_spot_em()
            stock_info = stock_data[stock_data['代码'] == stock_code].iloc[0]
            return float(stock_info['最新价'])
        except:
            return None 