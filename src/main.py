"""
Pinterest 下载器主控制器
协调各个模块完成下载任务
"""

import time
import os
from datetime import datetime
from typing import Optional
from src.core.config_manager import ConfigManager
from src.core.logger import logger
from src.core.browser_controller import BrowserController
from src.core.downloader import ImageDownloader
from src.utils.excel_exporter import ExcelExporter
from src.utils.helpers import estimate_remaining_time, format_number


class PinterestDownloader:
    """Pinterest 下载器主控制器"""
    
    def __init__(self, config_path: str = "config.json"):
        """
        初始化下载器
        
        Args:
            config_path: 配置文件路径
        """
        # 加载配置
        self.config_manager = ConfigManager(config_path)
        
        if not self.config_manager.validate():
            raise ValueError("配置文件验证失败")
        
        # 初始化日志
        log_file = self.config_manager.get('logging.file', 'pinterest_downloader.log')
        log_level = self.config_manager.get('logging.level', 'INFO')
        logger.setup_logger(log_file, log_level)
        
        # 初始化浏览器控制器
        self.browser = BrowserController()
        
        # 初始化下载器
        self.downloader = ImageDownloader(self.config_manager.config)
        
        # 初始化Excel导出器
        excel_path = os.path.join(
            self.config_manager.get('download.save_path', './downloads'),
            'download_report.xlsx'
        )
        self.excel_exporter = ExcelExporter(excel_path)
        
        # 状态标记
        self.is_running = False
        self.should_stop = False
        
        logger.info("Pinterest 下载器已初始化")
    
    def start(self) -> dict:
        """
        开始下载任务
        
        Returns:
            下载统计信息
        """
        if self.is_running:
            logger.warning("下载任务已在运行中")
            return {}
        
        self.is_running = True
        self.should_stop = False
        
        start_time = time.time()
        
        try:
            # 检查 Playwright
            if not self.browser.check_playwright_installed():
                raise RuntimeError("Playwright 未安装，请运行: pip install playwright && playwright install chromium")
            
            # 获取配置
            keywords = self.config_manager.get('search.keywords', 'UI设计')
            min_likes = self.config_manager.get('search.min_likes', 500)
            max_results = self.config_manager.get('search.max_results', 100)
            scroll_delay = self.config_manager.get('search.scroll_delay', 2)
            
            # 为本次任务创建独立文件夹
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            task_folder_name = f"{keywords.replace(' ', '_')}_{timestamp}"
            base_save_path = self.config_manager.get('download.save_path', './downloads')
            task_save_path = os.path.join(base_save_path, task_folder_name)
            
            # 创建任务文件夹
            if not os.path.exists(task_save_path):
                os.makedirs(task_save_path)
                logger.info(f"创建任务文件夹: {task_save_path}")
            
            # 更新下载器的保存路径
            self.downloader.save_path = task_save_path
            self.downloader._ensure_directory_exists(task_save_path)
            
            # 更新Excel导出器的输出路径
            excel_path = os.path.join(task_save_path, 'download_report.xlsx')
            self.excel_exporter.output_path = excel_path
            logger.info(f"Excel报告路径: {excel_path}")
            
            # 记录任务开始
            logger.log_download_start(keywords, min_likes, max_results)
            
            # 打开搜索页面
            if not self.browser.open_pinterest_search(keywords):
                raise RuntimeError("无法打开 Pinterest 搜索页面")
            
            # 滚动加载内容
            # 根据需要下载的数量决定滚动次数，每次滚动大约加载20-30个Pin
            scroll_times = max(3, (max_results // 25) + 1)
            self.browser.scroll_to_load_more(scroll_times, scroll_delay)
            
            # 等待内容加载完成
            time.sleep(3)
            logger.info("等待页面内容加载完成...")
            
            # 从搜索页提取Pin基本信息（URL和图片链接，不含点赞数）
            pins = self.browser.extract_pin_basic_info()
            
            if not pins:
                logger.warning("未找到任何 Pin")
            else:
                logger.info(f"找到 {len(pins)} 个 Pin，开始逐个提取点赞数并判断下载")
                
                # 边提取边判断边下载
                downloaded_count = 0
                processed_count = 0
                
                for i, pin in enumerate(pins):
                    if self.should_stop:
                        logger.info("用户终止下载")
                        break
                    
                    # 检查是否已达到最大下载数量
                    if downloaded_count >= max_results:
                        logger.info(f"已达到最大下载数量: {max_results}")
                        break
                    
                    processed_count += 1
                    pin_url = pin.get('url')
                    
                    if not pin_url:
                        logger.debug(f"Pin {processed_count} 缺少URL，跳过")
                        continue
                    
                    # 显示进度
                    logger.info(f"[{processed_count}/{len(pins)}] 正在处理: {pin_url}")
                    
                    # 访问详情页获取点赞数
                    likes = self.browser.extract_likes_from_detail_page(pin_url)
                    pin['likes'] = likes
                    
                    logger.info(f"  └─ 点赞数: {likes}")
                    
                    # 判断是否符合条件
                    if likes < min_likes:
                        logger.info(f"  └─ 不符合条件（{likes} < {min_likes}），跳过")
                        continue
                    
                    # 符合条件，准备下载
                    logger.info(f"  └─ ✓ 符合条件（{likes} >= {min_likes}），开始下载")
                    
                    # 准备元数据
                    metadata = {
                        'category': keywords,
                        'likes': likes,
                        'title': pin.get('title', '')
                    }
                    
                    # 下载图片
                    result = self.downloader.download_image(pin, metadata)
                    
                    if result:
                        downloaded_count += 1
                        logger.info(f"  └─ ✓ 下载成功: {os.path.basename(result)}")
                        logger.info(f"已下载进度: {downloaded_count}/{max_results}")
                        
                        # 添加到Excel报告
                        self.excel_exporter.add_record(
                            image_path=result,
                            likes=likes,
                            original_url=pin_url,
                            filename=os.path.basename(result)
                        )
                    
                    # 短暂延迟
                    if downloaded_count < max_results and processed_count < len(pins):
                        time.sleep(0.5)
                
                logger.info(f"✓ 处理完成：共处理 {processed_count} 个Pin，下载 {downloaded_count} 张图片")
            # 保存Excel报告
            if self.downloader.download_count > 0:
                self.excel_exporter.save()
                logger.info(f"Excel报告包含 {self.excel_exporter.get_record_count()} 条记录")
            
            # 统计信息
            elapsed_time = time.time() - start_time
            stats = {
                'total_found': len(pins),
                'total_downloaded': self.downloader.download_count,
                'elapsed_time': elapsed_time,
                'excel_path': self.excel_exporter.output_path if self.downloader.download_count > 0 else None
            }
            
            # 记录任务完成
            logger.log_download_complete(stats['total_downloaded'], elapsed_time)
            
            return stats
            
        except Exception as e:
            logger.error(f"下载任务失败: {e}")
            raise
        
        finally:
            # 清理
            self.browser.close()
            self.is_running = False
    
    def stop(self):
        """停止下载任务"""
        if self.is_running:
            logger.info("正在停止下载任务...")
            self.should_stop = True
    
    def get_progress(self) -> dict:
        """
        获取当前进度
        
        Returns:
            进度信息字典
        """
        stats = self.downloader.get_stats()
        max_results = self.config_manager.get('search.max_results', 100)
        
        completed = stats['total_downloaded']
        total = max_results
        progress_percent = (completed / total * 100) if total > 0 else 0
        
        return {
            'completed': completed,
            'total': total,
            'percent': progress_percent,
            'is_running': self.is_running
        }


def main():
    """命令行主程序入口"""
    import sys
    
    print("=" * 60)
    print("Pinterest 高赞图片下载器 v1.0")
    print("=" * 60)
    print()
    
    # 法律声明
    print("⚠️  重要声明:")
    print("本工具仅供个人学习和研究使用")
    print("请遵守 Pinterest 服务条款，尊重原创者版权")
    print("不得用于商业目的或侵犯他人权益")
    print()
    
    # 获取配置文件路径
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.json"
    
    try:
        # 创建下载器
        downloader = PinterestDownloader(config_path)
        
        # 显示配置
        print("当前配置:")
        print(f"  搜索关键词: {downloader.config_manager.get('search.keywords')}")
        print(f"  最低点赞数: {format_number(downloader.config_manager.get('search.min_likes'))}")
        print(f"  最大下载数: {format_number(downloader.config_manager.get('search.max_results'))}")
        print(f"  保存路径: {downloader.config_manager.get('download.save_path')}")
        print()
        
        # 确认开始
        response = input("是否开始下载？(y/n): ")
        if response.lower() != 'y':
            print("已取消")
            return
        
        print()
        print("开始下载...")
        print()
        
        # 开始下载
        stats = downloader.start()
        
        # 显示结果
        print()
        print("=" * 60)
        print("下载完成！")
        print(f"找到 Pin: {stats.get('total_found', 0)} 个")
        print(f"已下载: {stats.get('total_downloaded', 0)} 张")
        print(f"总耗时: {stats.get('elapsed_time', 0):.2f} 秒")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n用户中断，正在清理...")
        downloader.stop()
    except Exception as e:
        print(f"\n错误: {e}")
        logger.error(f"程序异常: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
