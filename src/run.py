from web_app import app
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        logger.info("启动Web应用...")
        app.run(host='0.0.0.0', port=5001, debug=True)
    except KeyboardInterrupt:
        logger.info("正在关闭应用...")
        logger.info("应用已关闭") 