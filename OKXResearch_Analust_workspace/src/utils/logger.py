import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

def setup_logger(name="OKXResearch", log_file=None, level=logging.INFO):
    """
    配置并返回一个 logger 实例
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重复添加 handler
    if logger.handlers:
        return logger

    # 文件日志格式：包含时间、模块名、级别，详细记录
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 控制台日志格式：只显示消息，保持界面清爽
    # 因为我们使用了 Rich UI，不需要在控制台重复显示时间戳等元数据
    console_formatter = logging.Formatter(
        '%(message)s'
    )

    # 控制台 Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # 文件 Handler (如果指定)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 使用 RotatingFileHandler 限制日志大小
        # maxBytes=10MB, backupCount=5 (保留5个备份文件)
        file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=10*1024*1024, 
            backupCount=5, 
            encoding='utf-8'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger
