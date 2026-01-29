"""
图片下载管理模块
负责下载和保存图片
"""

import os
import requests
import time
from typing import Dict, Set, Optional
from PIL import Image
from io import BytesIO
from .logger import logger


class ImageDownloader:
    """图片下载管理器"""
    
    def __init__(self, config: Dict):
        """
        初始化下载器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.downloaded_urls: Set[str] = set()  # 已下载的URL集合，用于去重
        self.download_count = 0
        
        # 创建保存目录
        self.save_path = config.get('download', {}).get('save_path', './downloads')
        self._ensure_directory_exists(self.save_path)
        
        logger.info(f"图片下载器已初始化，保存路径: {self.save_path}")
    
    def _ensure_directory_exists(self, directory: str):
        """
        确保目录存在，不存在则创建
        
        Args:
            directory: 目录路径
        """
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"创建目录: {directory}")
    
    def should_download(self, likes: int) -> bool:
        """
        判断是否应该下载该图片
        
        Args:
            likes: 点赞数
        
        Returns:
            是否应该下载
        """
        min_likes = self.config.get('search', {}).get('min_likes', 500)
        return likes >= min_likes
    
    def download_image(self, url: str, metadata: Dict) -> Optional[str]:
        """
        下载单张图片
        
        Args:
            url: 图片URL（可以传递Pin数据字典）
            metadata: 元数据，包含点赞数、类目等信息
        
        Returns:
            保存的文件路径，失败返回None
        """
        # 如果url是字典（Pin数据），提取实际URL
        if isinstance(url, dict):
            pin_data = url
            # 优先使用高质量图片URL
            url = pin_data.get('image_url_hq') or pin_data.get('image_url')
            # 合并metadata
            if 'likes' in pin_data:
                metadata = {**metadata, **pin_data}
        
        if not url:
            logger.debug("没有有效的图片URL")
            return None
        
        # 检查是否已下载
        if url in self.downloaded_urls:
            logger.debug(f"跳过重复图片: {url}")
            return None
        
        # 检查点赞数是否达标
        likes = metadata.get('likes', 0)
        if not self.should_download(likes):
            logger.debug(f"点赞数不足，跳过: {likes} < {self.config.get('search', {}).get('min_likes')}")
            return None
        
        try:
            # 下载图片
            logger.debug(f"开始下载: {url}")
            response = requests.get(url, timeout=30, headers={
                'User-Agent': self._get_user_agent(),
                'Referer': 'https://www.pinterest.com/'
            })
            response.raise_for_status()
            
            # 检查图片格式
            img = Image.open(BytesIO(response.content))
            
            # 检查分辨率
            if not self._check_resolution(img):
                logger.debug(f"分辨率不足，跳过: {img.size}")
                return None
            
            # 生成文件名
            filename = self._generate_filename(metadata)
            filepath = os.path.join(self.save_path, filename)
            
            # 保存图片
            img.save(filepath)
            
            # 记录已下载
            self.downloaded_urls.add(url)
            self.download_count += 1
            
            logger.log_image_download(filename, likes, True)
            return filepath
            
        except requests.RequestException as e:
            logger.error(f"下载失败 (网络错误): {url} - {e}")
            return None
        except Exception as e:
            logger.error(f"下载失败: {url} - {e}")
            return None
    
    def _check_resolution(self, img: Image.Image) -> bool:
        """
        检查图片分辨率是否满足要求
        
        Args:
            img: PIL Image 对象
        
        Returns:
            是否满足分辨率要求
        """
        min_res = self.config.get('download', {}).get('min_resolution', {})
        min_width = min_res.get('width', 0)
        min_height = min_res.get('height', 0)
        
        width, height = img.size
        return width >= min_width and height >= min_height
    
    def _generate_filename(self, metadata: Dict) -> str:
        """
        生成文件名
        
        Args:
            metadata: 元数据
        
        Returns:
            文件名
        """
        naming_format = self.config.get('download', {}).get('naming_format', '{category}_{likes}_{index}')
        image_format = self.config.get('download', {}).get('image_format', 'jpg')
        
        # 替换占位符
        filename = naming_format.format(
            category=metadata.get('category', 'pin').replace(' ', '_'),
            likes=metadata.get('likes', 0),
            index=f"{self.download_count + 1:04d}"  # 4位数字，补零
        )
        
        # 清理文件名中的非法字符
        filename = self._sanitize_filename(filename)
        
        return f"{filename}.{image_format}"
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        清理文件名中的非法字符
        
        Args:
            filename: 原始文件名
        
        Returns:
            清理后的文件名
        """
        # Windows 不允许的字符
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename
    
    def _get_user_agent(self) -> str:
        """
        获取 User-Agent
        
        Returns:
            User-Agent 字符串
        """
        user_agents = self.config.get('behavior', {}).get('user_agents', [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        ])
        return user_agents[0] if user_agents else ''
    
    def get_stats(self) -> Dict:
        """
        获取下载统计信息
        
        Returns:
            统计信息字典
        """
        return {
            'total_downloaded': self.download_count,
            'unique_urls': len(self.downloaded_urls)
        }


if __name__ == "__main__":
    # 测试下载器
    config = {
        'search': {'min_likes': 100},
        'download': {
            'save_path': './test_downloads',
            'naming_format': 'test_{likes}_{index}',
            'image_format': 'jpg',
            'min_resolution': {'width': 800, 'height': 600}
        },
        'behavior': {
            'user_agents': ['Mozilla/5.0']
        }
    }
    
    downloader = ImageDownloader(config)
    
    # 测试URL（使用一个公开的测试图片）
    test_url = "https://via.placeholder.com/1000x800.jpg"
    test_metadata = {
        'category': 'test',
        'likes': 1500
    }
    
    result = downloader.download_image(test_url, test_metadata)
    print(f"\n下载结果: {result}")
    print(f"统计信息: {downloader.get_stats()}")
