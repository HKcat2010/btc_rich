import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

class ImmediateDiskLogger:
    """
    支持多级日志记录并确保实时落盘的日志模块
    """
    
    def __init__(self, 
                 name: str = "app", 
                 log_dir: str = "logs",
                 log_level: int = logging.DEBUG,
                 max_bytes: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5
                 std_redirect: bool = True):
        """
        初始化日志记录器
        
        :param name: 日志记录器名称
        :param log_dir: 日志目录路径
        :param log_level: 日志级别
        :param max_bytes: 单个日志文件最大字节数
        :param backup_count: 保留的日志备份数量
        """
        # 创建日志目录
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建日志记录器
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        
        # 设置日志格式
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)-8s %(filename)s:%(lineno)d  %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 创建文件处理器（确保立即落盘）
        log_file = self.log_dir / f"{name}"
        file_handler = RotatingFileHandler(
            log_file,
            mode='a',
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        
        # 强制立即刷新缓冲区
        file_handler.stream.flush = lambda: os.fsync(file_handler.stream.fileno())
        
        # 添加处理器
        self.logger.addHandler(file_handler)
        
        # 添加控制台处理器（可选）
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(log_level)
        self.logger.addHandler(console_handler)
        if (std_redirect):
            sys.stdout = self.logger.handlers[0].stream
            sys.stderr = self.logger.handlers[0].stream
        self.logger.info(f"日志文件 {name} 初始化完成")
    
    def debug(self, message: str):
        """记录调试信息"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """记录常规信息"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """记录警告信息"""
        self.logger.warning(message)
    
    def error(self, message: str, exc_info: bool = False):
        """记录错误信息"""
        self.logger.error(message, exc_info=exc_info)
    
    def critical(self, message: str, exc_info: bool = False):
        """记录严重错误信息"""
        self.logger.critical(message, exc_info=exc_info)
    
    def exception(self, message: str):
        """记录异常信息（自动包含堆栈跟踪）"""
        self.logger.exception(message)