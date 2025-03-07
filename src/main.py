import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.strategies.hot_theme_strategy import HotThemeStrategy
import time
import schedule
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading.log'),
        logging.StreamHandler()
    ]
)

def run_strategy():
    """运行交易策略"""
    try:
        strategy = HotThemeStrategy(initial_capital=1000000)  # 100万初始资金
        strategy.run_daily_strategy()
        
        # 获取并记录策略状态
        status = strategy.get_strategy_status()
        logging.info(f"策略执行完成")
        logging.info(f"当前资金: {status['current_capital']:.2f}")
        logging.info(f"持仓数量: {status['position_count']}")
        for code, position in status['positions'].items():
            logging.info(f"持仓股票: {code}, 数量: {position['quantity']:.0f}, "
                        f"成本: {position['price']:.2f}")
                        
    except Exception as e:
        logging.error(f"策略执行出错: {e}")

def main():
    logging.info("启动交易系统...")
    
    # 设置定时任务
    schedule.every().day.at("09:30").do(run_strategy)  # 开盘时运行
    schedule.every().day.at("14:30").do(run_strategy)  # 收盘前运行
    
    # 立即运行一次
    run_strategy()
    
    # 持续运行定时任务
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main() 