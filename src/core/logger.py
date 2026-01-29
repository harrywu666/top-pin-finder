"""
日志管理模块
负责应用程序的日志记录
"""

import logging
import os
from datetime import datetime
from typing import Optional


class Logger:
    """应用程序日志管理器"""
    
    _instance: Optional['Logger'] = None
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化日志器"""
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.logger = None
            self._setup_default_logger()
    
    def _setup_default_logger(self):
        """设置默认日志器"""
        self.setup_logger("pinterest_downloader.log", "INFO")
    
    def setup_logger(self, log_file: str = "app.log", level: str = "INFO"):
        """
        设置日志器
        
        Args:
            log_file: 日志文件路径
            level: 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
        """
        # 创建日志器
        self.logger = logging.getLogger("PinterestDownloader")
        self.logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        
        # 移除已存在的处理器
        self.logger.handlers.clear()
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_format)
        
        # 创建文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        
        # 添加处理器
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        
        self.info(f"日志系统已初始化，日志文件: {log_file}")
    
    def debug(self, message: str):
        """记录调试信息"""
        if self.logger:
            self.logger.debug(message)
    
    def info(self, message: str):
        """记录普通信息"""
        if self.logger:
            self.logger.info(message)
    
    def warning(self, message: str):
        """记录警告信息"""
        if self.logger:
            self.logger.warning(message)
    
    def error(self, message: str):
        """记录错误信息"""
        if self.logger:
            self.logger.error(message)
    
    def critical(self, message: str):
        """记录严重错误信息"""
        if self.logger:
            self.logger.critical(message)
    
    def log_download_start(self, keyword: str, min_likes: int, max_results: int):
        """记录下载任务开始"""
        self.info(f"="*50)
        self.info(f"开始新的下载任务")
        self.info(f"搜索关键词: {keyword}")
        self.info(f"最低点赞数: {min_likes}")
        self.info(f"最大下载数: {max_results}")
        self.info(f"="*50)
    
    def log_download_complete(self, total_downloaded: int, total_time: float):
        """记录下载任务完成"""
        self.info(f"="*50)
        self.info(f"下载任务完成")
        self.info(f"总下载数: {total_downloaded}")
        self.info(f"总耗时: {total_time:.2f}秒")
        self.info(f"="*50)
    
    def log_image_download(self, filename: str, likes: int, success: bool = True):
        """记录单张图片下载"""
        if success:
            self.info(f"✓ 下载成功: {filename} (点赞数: {likes})")
        else:
            self.error(f"✗ 下载失败: {filename}")


# 创建全局日志实例
logger = Logger()


if __name__ == "__main__":
    # 测试日志功能
    logger.debug("这是调试信息")
    logger.info("这是普通信息")
    logger.warning("这是警告信息")
    logger.error("这是错误信息")
    
    logger.log_download_start("UI设计", 500, 100)
    logger.log_image_download("ui_design_1234.jpg", 1234, True)
    logger.log_image_download("ui_design_5678.jpg", 5678, False)
    logger.log_download_complete(45, 120.5)
