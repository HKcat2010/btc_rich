import logging
import os
from logging.handlers import RotatingFileHandler
from concurrent_log_handler import ConcurrentRotatingFileHandler
from pathlib import Path

class SingletonLogger:
    _instance = None

    def __new__(cls, *args, **kwargs):
        """单例模式实现，确保全局唯一日志实例"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__init_logger()  # 仅初始化一次
        return cls._instance

    def __init_logger(self):
        """配置日志器（线程安全 + 多进程安全）"""
        self.logger = logging.getLogger("SingletonLogger")
        self.logger.setLevel(logging.DEBUG)  # 默认日志级别

        # 日志格式（含时间戳、进程ID、日志级别）
        formatter = logging.Formatter(
            "%(asctime)s.%(msecs)03d | PID:%(process)d | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # 多进程安全的文件处理器（追加模式，崩溃后自动恢复）
        log_path = Path(time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(time.time())) + ".log").absolute()
        file_handler = ConcurrentRotatingFileHandler(
            filename=log_path,
            mode="a",  # 追加模式，确保崩溃后继续写入[6,8](@ref)
            maxBytes=10 * 1024 * 1024,  # 单个日志最大10MB
            backupCount=5,
            encoding="utf-8",
            use_gzip=False
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)  # 文件日志级别

        # 强制每次写入后刷新到磁盘（避免缓存丢失）
        def safe_flush():
            file_handler.stream.flush()
            os.fsync(file_handler.stream.fileno())  # 确保物理落盘[1](@ref)
        file_handler.flush = safe_flush

        # 控制台处理器（可选）
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.DEBUG)

        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    # 日志记录方法
    def debug(self, msg):
        self.logger.debug(msg)
    
    def info(self, msg):
        self.logger.info(msg)
    
    def warning(self, msg):
        self.logger.warning(msg)
    
    def error(self, msg, exc_info=False):
        self.logger.error(msg, exc_info=exc_info)  # 自动捕获异常堆栈[7](@ref)
    
    def critical(self, msg, exc_info=False):
        self.logger.critical(msg, exc_info=exc_info)