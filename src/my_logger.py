import os
import logging
from concurrent_log_handler import ConcurrentRotatingFileHandler

# 创建日志目录
log_dir = './log'
os.makedirs(log_dir, exist_ok=True)

# 创建 logger
logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)

# 控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 文件处理器（多进程安全）
file_handler = ConcurrentRotatingFileHandler(
    os.path.join(log_dir, 'my_log.log'), maxBytes=1024 * 1024 * 5, backupCount=5, encoding='utf-8'
)
file_handler.setLevel(logging.DEBUG)

# 设置格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# 添加到 logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# 测试输出
logger.debug('这是 debug 日志')
