from flask import Flask, render_template, jsonify
from strategies.hot_theme_strategy import HotThemeStrategy
from datetime import datetime
import json

app = Flask(__name__)
strategy = HotThemeStrategy(initial_capital=1000000)

def get_risk_class(risk_score):
    if risk_score >= 0.7:
        return "risk-high"
    elif risk_score >= 0.4:
        return "risk-medium"
    else:
        return "risk-low"

@app.route('/')
def index():
    try:
        # 获取策略状态
        status = strategy.get_strategy_status()
        
        # 准备持仓数据
        positions = []
        for code, position in status['positions'].items():
            current_price = strategy.stock_selector.get_current_price(code)
            if current_price is None:
                current_price = position['price']
            
            profit_pct = (current_price - position['price']) / position['price'] * 100
            risk_score = strategy.risk_calculator.calculate_risk_score(code)
            
            positions.append({
                'code': code,
                'name': strategy.stock_selector.get_stock_name(code),
                'quantity': int(position['quantity']),
                'cost_price': round(position['price'], 2),
                'current_price': round(current_price, 2),
                'profit_pct': round(profit_pct, 2),
                'risk_score': round(risk_score, 2),
                'risk_class': get_risk_class(risk_score)
            })
        
        return render_template('index.html',
                            current_capital=round(status['current_capital'], 2),
                            position_count=status['position_count'],
                            positions=positions,
                            risk_dates=json.dumps([]),
                            risk_scores=json.dumps([]),
                            recent_trades=[])
    except Exception as e:
        print(f"Error in index route: {e}")
        return render_template('index.html',
                            current_capital=1000000.00,
                            position_count=0,
                            positions=[],
                            risk_dates=json.dumps([]),
                            risk_scores=json.dumps([]),
                            recent_trades=[])

@app.route('/api/run_strategy')
def run_strategy():
    try:
        strategy.run_daily_strategy()
        status = strategy.get_strategy_status()
        return jsonify({
            'success': True,
            'current_capital': round(status['current_capital'], 2),
            'position_count': status['position_count'],
            'message': '策略执行成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'策略执行失败: {str(e)}'
        })

@app.route('/api/update')
def update():
    try:
        status = strategy.get_strategy_status()
        return jsonify({
            'current_capital': round(status['current_capital'], 2),
            'position_count': status['position_count'],
            'risk_dates': [],
            'risk_scores': []
        })
    except Exception as e:
        return jsonify({
            'current_capital': 1000000.00,
            'position_count': 0,
            'risk_dates': [],
            'risk_scores': []
        })

if __name__ == '__main__':
    app.run(debug=True, port=5001) 