"""
配置管理模块
负责加载、保存和验证配置文件
"""

import json
import os
from typing import Dict, Any


class ConfigManager:
    """配置文件管理器"""
    
    def __init__(self, config_path: str = "config.json"):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """
        加载配置文件
        
        Returns:
            配置字典
        """
        if not os.path.exists(self.config_path):
            print(f"警告: 配置文件 {self.config_path} 不存在，使用默认配置")
            return self._get_default_config()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"成功加载配置文件: {self.config_path}")
            return config
        except json.JSONDecodeError as e:
            print(f"错误: 配置文件格式错误 - {e}")
            print("使用默认配置")
            return self._get_default_config()
        except Exception as e:
            print(f"错误: 无法读取配置文件 - {e}")
            return self._get_default_config()
    
    def save_config(self, config: Dict[str, Any] = None):
        """
        保存配置文件
        
        Args:
            config: 要保存的配置字典，如果为None则保存当前配置
        """
        if config is None:
            config = self.config
        
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            print(f"配置已保存到: {self.config_path}")
        except Exception as e:
            print(f"错误: 无法保存配置文件 - {e}")
    
    def get(self, key_path: str, default=None):
        """
        获取配置值，支持嵌套键（用点号分隔）
        
        Args:
            key_path: 配置键路径，例如 "search.min_likes"
            default: 默认值
        
        Returns:
            配置值
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any):
        """
        设置配置值，支持嵌套键（用点号分隔）
        
        Args:
            key_path: 配置键路径，例如 "search.min_likes"
            value: 要设置的值
        """
        keys = key_path.split('.')
        config = self.config
        
        # 遍历到倒数第二层
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # 设置最后一层的值
        config[keys[-1]] = value
    
    @staticmethod
    def _get_default_config() -> Dict[str, Any]:
        """
        获取默认配置
        
        Returns:
            默认配置字典
        """
        return {
            "pinterest": {
                "login_required": False,
                "session_cookie": ""
            },
            "search": {
                "keywords": "UI设计",
                "min_likes": 500,
                "max_results": 100,
                "scroll_delay": 2
            },
            "download": {
                "save_path": "./downloads",
                "naming_format": "{category}_{likes}_{index}",
                "image_format": "jpg",
                "min_resolution": {
                    "width": 800,
                    "height": 600
                }
            },
            "behavior": {
                "random_delay_min": 1,
                "random_delay_max": 3,
                "user_agents": [
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                ]
            },
            "logging": {
                "level": "INFO",
                "file": "pinterest_downloader.log"
            }
        }
    
    def validate(self) -> bool:
        """
        验证配置的有效性
        
        Returns:
            配置是否有效
        """
        required_keys = [
            "search.keywords",
            "search.min_likes",
            "search.max_results",
            "download.save_path"
        ]
        
        for key_path in required_keys:
            if self.get(key_path) is None:
                print(f"错误: 缺少必需的配置项 {key_path}")
                return False
        
        # 验证数值范围
        min_likes = self.get("search.min_likes")
        if not isinstance(min_likes, int) or min_likes < 0:
            print("错误: search.min_likes 必须是非负整数")
            return False
        
        max_results = self.get("search.max_results")
        if not isinstance(max_results, int) or max_results <= 0:
            print("错误: search.max_results 必须是正整数")
            return False
        
        print("配置验证通过")
        return True


if __name__ == "__main__":
    # 测试配置管理器
    config = ConfigManager()
    print("\n当前配置:")
    print(json.dumps(config.config, ensure_ascii=False, indent=2))
    
    print("\n验证配置:")
    config.validate()
    
    print("\n获取配置值:")
    print(f"搜索关键词: {config.get('search.keywords')}")
    print(f"最低点赞数: {config.get('search.min_likes')}")
    
    print("\n设置配置值:")
    config.set('search.keywords', '建筑设计')
    print(f"新的搜索关键词: {config.get('search.keywords')}")
