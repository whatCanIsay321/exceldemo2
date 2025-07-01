import logging
from logging.handlers import RotatingFileHandler
# 创建 logger
logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)  # 设置日志级别为 DEBUG

# 创建控制台处理器并设置级别为 INFO
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 创建文件处理器并设置级别为 DEBUG

file_handler = RotatingFileHandler('./log/my_log.log', maxBytes=1024 * 1024 * 5, backupCount=5,encoding='utf-8' )
file_handler.setLevel(logging.DEBUG)

# 定义日志输出格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# 添加处理器到 logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# 生成不同级别的日志
# logger.debug('这是 debug 日志')
# logger.info('这是 info 日志')
# logger.warning('这是 warning 日志')
# logger.error('这是 error 日志')
# logger.critical('这是 critical 日志')
