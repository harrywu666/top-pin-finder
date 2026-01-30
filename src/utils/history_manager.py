"""
历史记录管理模块
记录已下载的Pin ID,避免重复下载
"""

import json
import os
from typing import Set
from datetime import datetime
from ..core.logger import logger


class HistoryManager:
    """历史记录管理器 - 跟踪已下载的Pin,避免重复"""
    
    def __init__(self, history_file: str = "./downloads/.download_history.json"):
        """
        初始化历史记录管理器
        
        Args:
            history_file: 历史记录文件路径
        """
        self.history_file = history_file
        self.downloaded_pins: Set[str] = set()  # 已下载的Pin ID集合
        
        # 加载历史记录
        self._load_history()
        
        logger.info(f"历史记录管理器已初始化,已记录 {len(self.downloaded_pins)} 个Pin")
    
    def _load_history(self):
        """从文件加载历史记录"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.downloaded_pins = set(data.get('pins', []))
                    logger.info(f"✓ 已加载历史记录: {len(self.downloaded_pins)} 个Pin")
            else:
                logger.info("历史记录文件不存在,将创建新文件")
        except Exception as e:
            logger.warning(f"加载历史记录失败: {e},将使用空历史")
            self.downloaded_pins = set()
    
    def _save_history(self):
        """保存历史记录到文件"""
        try:
            # 确保目录存在
            history_dir = os.path.dirname(self.history_file)
            if history_dir and not os.path.exists(history_dir):
                os.makedirs(history_dir)
            
            # 保存数据
            data = {
                'pins': list(self.downloaded_pins),
                'total_count': len(self.downloaded_pins),
                'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"历史记录已保存: {len(self.downloaded_pins)} 个Pin")
            return True
            
        except Exception as e:
            logger.error(f"保存历史记录失败: {e}")
            return False
    
    def is_downloaded(self, pin_id: str) -> bool:
        """
        检查Pin是否已经下载过
        
        Args:
            pin_id: Pin ID
        
        Returns:
            是否已下载
        """
        return pin_id in self.downloaded_pins
    
    def add_pin(self, pin_id: str, auto_save: bool = True):
        """
        添加已下载的Pin ID
        
        Args:
            pin_id: Pin ID
            auto_save: 是否自动保存到文件
        """
        if pin_id and pin_id not in self.downloaded_pins:
            self.downloaded_pins.add(pin_id)
            logger.debug(f"添加Pin到历史记录: {pin_id}")
            
            # 自动保存
            if auto_save:
                self._save_history()
    
    def get_count(self) -> int:
        """
        获取历史记录数量
        
        Returns:
            已记录的Pin数量
        """
        return len(self.downloaded_pins)
    
    def clear_history(self):
        """清空历史记录"""
        self.downloaded_pins.clear()
        self._save_history()
        logger.info("历史记录已清空")
    
    def save(self):
        """手动保存历史记录"""
        return self._save_history()


if __name__ == "__main__":
    # 测试历史管理器
    manager = HistoryManager("./test_history.json")
    
    # 添加测试Pin
    manager.add_pin("123456789")
    manager.add_pin("987654321")
    
    # 检查是否存在
    print(f"Pin 123456789 已下载: {manager.is_downloaded('123456789')}")
    print(f"Pin 111111111 已下载: {manager.is_downloaded('111111111')}")
    
    # 显示统计
    print(f"总共记录: {manager.get_count()} 个Pin")
