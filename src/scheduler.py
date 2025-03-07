import schedule
import time
from strategies.hot_theme_strategy import HotThemeStrategy
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class StrategyScheduler:
    def __init__(self):
        self.strategy = HotThemeStrategy(initial_capital=1000000)
        self.setup_schedule()
        
    def setup_schedule(self):
        """设置定时任务"""
        # 每个交易日9:30运行策略
        schedule.every().day.at("09:30").do(self.run_strategy)
        # 每个交易日15:00进行收盘总结
        schedule.every().day.at("15:00").do(self.daily_summary)
        
    def run_strategy(self):
        """运行策略"""
        try:
            if self.is_trading_day():
                logger.info("开始运行策略...")
                self.strategy.run_daily_strategy()
                logger.info("策略运行完成")
        except Exception as e:
            logger.error(f"策略运行出错: {e}")
            
    def daily_summary(self):
        """每日总结"""
        try:
            if self.is_trading_day():
                status = self.strategy.get_strategy_status()
                logger.info("=== 每日总结 ===")
                logger.info(f"当前资金: {status['current_capital']:.2f}")
                logger.info(f"持仓数量: {status['position_count']}")
                logger.info("持仓明细:")
                for code, position in status['positions'].items():
                    logger.info(f"  {code}: {position['quantity']} 股, 成本价: {position['price']:.2f}")
        except Exception as e:
            logger.error(f"生成每日总结时出错: {e}")
            
    def is_trading_day(self):
        """判断是否为交易日"""
        # TODO: 实现交易日判断逻辑
        # 这里可以使用 akshare 获取交易日历
        return True
        
    def run(self):
        """运行调度器"""
        logger.info("启动策略调度器...")
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次

if __name__ == "__main__":
    scheduler = StrategyScheduler()
    scheduler.run() 