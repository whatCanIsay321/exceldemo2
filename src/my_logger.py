import os
import logging
from concurrent_log_handler import ConcurrentRotatingFileHandler
from logging.handlers import RotatingFileHandler

# 创建日志目录

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.abspath(os.path.join(BASE_DIR, "../log"))
os.makedirs(LOG_DIR, exist_ok=True)
# 创建 logger
logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)

if not logger.handlers:

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # 文件处理器（多进程安全）
    file_handler = ConcurrentRotatingFileHandler(
        os.path.join(LOG_DIR, 'my_log.log'), maxBytes=1024 * 1024 * 5, backupCount=5, encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)

    # 设置格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # 添加到 logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


