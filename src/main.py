"""
Pinterest 下载器主控制器
协调各个模块完成任务
"""

import time
import random
import os
import re
from datetime import datetime
from typing import Optional, List, Dict
from src.core.config_manager import ConfigManager
from src.core.logger import logger
from src.core.browser_controller import BrowserController
from src.utils.google_sheets_exporter import GoogleSheetsExporter
from src.utils.history_manager import HistoryManager
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
        
        # 初始化Google Sheets导出器(如果启用)
        gs_enabled = self.config_manager.get('google_sheets.enabled', False)
        if gs_enabled:
            spreadsheet_id = self.config_manager.get('google_sheets.spreadsheet_id')
            credentials_file = self.config_manager.get('google_sheets.credentials_file')
            self.sheets_exporter = GoogleSheetsExporter(spreadsheet_id, credentials_file)
        else:
            self.sheets_exporter = None
        
        # 初始化历史记录管理器
        history_file = self.config_manager.get('search.history_file', './downloads/.download_history.json')
        self.history_manager = HistoryManager(history_file)
        
        # 状态标记
        self.is_running = False
        self.should_stop = False
        
        logger.info("Pinterest 下载器已初始化")
    
    def start(self) -> dict:
        """
        开始任务 (改进的随机漫步模式 - 模拟真人浏览)
        
        Returns:
            统计信息
        """
        if self.is_running:
            logger.warning("任务已在运行中")
            return {}
        
        self.is_running = True
        self.should_stop = False
        
        start_time = time.time()
        
        try:
            # 检查 Playwright
            if not self.browser.check_playwright_installed():
                raise RuntimeError("Playwright 未安装，请运行: pip install playwright && playwright install chromium")
            
            # 获取配置
            keywords = self.config_manager.get('search.keywords')
            min_likes = self.config_manager.get('search.min_likes', 100)
            max_results = self.config_manager.get('search.max_results', 50)
            sort_by = self.config_manager.get('search.sort_by', 'relevance')
            enable_random = self.config_manager.get('search.enable_random', False)
            random_sort_prob = self.config_manager.get('search.random_sort_probability', 0.8)
            
            # 强化随机化策略:结合时间戳循环和随机选择
            if enable_random:
                sort_options = ['relevance', 'latest', 'popular']
                timestamp_sort = sort_options[int(time.time()) % 3]
                
                if random.random() < random_sort_prob:
                    original_sort = sort_by
                    available_sorts = [s for s in sort_options if s != original_sort]
                    sort_by = random.choice(available_sorts) if available_sorts else timestamp_sort
                    logger.info(f"🎲 强制随机排序: {original_sort} → {sort_by}")
                else:
                    if timestamp_sort != sort_by:
                        logger.info(f"🕐 时间戳循环排序: {sort_by} → {timestamp_sort}")
                        sort_by = timestamp_sort
            
            if not keywords:
                logger.error("搜索关键词为空")
                return {'success': False, 'error': '搜索关键词为空'}
            
            # 连接Google Sheets
            if self.sheets_exporter:
                if not self.sheets_exporter.connect():
                    raise RuntimeError("无法连接到Google Sheets")
                if not self.sheets_exporter.create_worksheet(keywords):
                    raise RuntimeError("无法创建Google Sheets工作表")
            
            # 记录任务开始
            logger.log_download_start(keywords, min_likes, max_results)
            
            recorded_count = 0
            visited_urls = set()
            consecutive_failures = 0
            
            # === 改进的候选池管理 ===
            # 主池：从搜索结果页获取的Pin（永不彻底耗尽，可滚动加载更多）
            main_pool = []  # 搜索结果的候选池
            # 副池：当前详情页的关联推荐
            related_pool = []  # 关联推荐候选池
            # 历史池：记录之前访问过的页面候选，用于"返回"
            history_pool = []  # 历史候选池，当副池耗尽时回退
            
            current_source = "search"  # 当前来源：search 或 related
            
            # 1. 初始搜索
            if not self.browser.open_pinterest_search(keywords, sort_by):
                raise RuntimeError("无法打开 Pinterest 搜索页面")
            
            # 2. 获取初始候选池
            logger.info("获取初始候选列表...")
            self.browser.scroll_to_load_more(2, 2)
            main_pool = self.browser.extract_pin_basic_info()
            
            if not main_pool:
                logger.warning("未找到任何初始内容")
                return {}
            
            logger.info(f"初始候选池: {len(main_pool)} 个Pin")
            
            # 随机漫步循环
            while recorded_count < max_results and not self.should_stop:
                
                # === 智能候选池选择 ===
                target_pin = None
                
                # 策略优先级：
                # 1. 优先从关联池选（深度优先，更像真人）
                # 2. 关联池空了，从历史池选（回退）
                # 3. 历史池也空了，从主池选（重新开始）
                
                # 过滤掉已访问的
                related_candidates = [p for p in related_pool if p.get('url') and p.get('url') not in visited_urls]
                history_candidates = [p for p in history_pool if p.get('url') and p.get('url') not in visited_urls]
                main_candidates = [p for p in main_pool if p.get('url') and p.get('url') not in visited_urls]
                
                if related_candidates:
                    # 有关联推荐，深度优先
                    target_pin = random.choice(related_candidates)
                    current_source = "related"
                    logger.info(f"🎯 从关联推荐选择 ({len(related_candidates)} 个候选)")
                elif history_candidates:
                    # 关联池空了，从历史池回退
                    target_pin = random.choice(history_candidates)
                    current_source = "history"
                    logger.info(f"⬅️ 从历史记录回退选择 ({len(history_candidates)} 个候选)")
                elif main_candidates:
                    # 都空了，从主池选
                    target_pin = random.choice(main_candidates)
                    current_source = "search"
                    logger.info(f"🔍 从搜索结果选择 ({len(main_candidates)} 个候选)")
                else:
                    # 所有池都空了，尝试滚动加载更多
                    logger.info("所有候选池耗尽，尝试滚动加载更多...")
                    self.browser.scroll_to_load_more(1, 2)
                    new_pins = self.browser.extract_pin_basic_info()
                    
                    if new_pins:
                        # 合并新加载的Pin到主池
                        existing_urls = {p.get('url') for p in main_pool}
                        new_unique_pins = [p for p in new_pins if p.get('url') and p.get('url') not in existing_urls]
                        if new_unique_pins:
                            main_pool.extend(new_unique_pins)
                            logger.info(f"✓ 加载了 {len(new_unique_pins)} 个新Pin")
                            continue
                    
                    # 真的没内容了，重新搜索
                    logger.info("候选池已彻底耗尽，重新搜索...")
                    if not self.browser.open_pinterest_search(keywords, sort_by):
                        break
                    self.browser.scroll_to_load_more(2, 2)
                    main_pool = self.browser.extract_pin_basic_info()
                    related_pool = []
                    history_pool = []
                    continue
                
                target_url = target_pin.get('url')
                visited_urls.add(target_url)
                
                logger.info(f"👣 随机漫步 -> 目标: {target_url}")
                
                # 4. 导航 (SPA跳转)
                if not self.browser.click_pin_and_wait(target_url):
                    logger.warning("跳转失败，尝试下一个")
                    consecutive_failures += 1
                    if consecutive_failures > 5:
                        logger.error("连续导航失败，重启浏览器")
                        self.browser.close()
                        self.browser.start_browser()
                        self.browser.open_pinterest_search(keywords, sort_by)
                        self.browser.scroll_to_load_more(2, 2)
                        main_pool = self.browser.extract_pin_basic_info()
                        related_pool = []
                        history_pool = []
                        consecutive_failures = 0
                    continue
                
                consecutive_failures = 0
                
                # 5. 分析当前的Pin (查看点赞数)
                current_likes = self.browser.extract_likes_from_current_page()
                logger.info(f"  └─ 当前Pin点赞数: {current_likes}")
                
                # 6. 判断并记录
                if current_likes >= min_likes:
                    pin_id = target_pin.get('pin_id', '')
                    if not pin_id:
                        match = re.search(r'/pin/(\d+)', target_url)
                        pin_id = match.group(1) if match else f"unknown_{int(time.time())}"

                    if not self.history_manager.is_downloaded(pin_id):
                        logger.info(f"  └─ ✨ 发现宝藏! ({current_likes} >= {min_likes})")
                        recorded_count += 1
                        
                        if self.sheets_exporter:
                            self.sheets_exporter.add_record(
                                index=recorded_count,
                                image_url=target_pin.get('image_url', ''),
                                likes=current_likes,
                                title=target_pin.get('title', 'Random Walk'),
                                pin_url=target_url
                            )
                        
                        self.history_manager.add_pin(pin_id, auto_save=True)
                        logger.info(f"已记录进度: {recorded_count}/{max_results}")
                    else:
                        logger.info("  └─ 已记录过，跳过")
                else:
                    logger.info(f"  └─ 点赞不足，继续寻找")
                
                # 7. 发现：获取关联图片作为下一步的候选
                logger.info("  └─ 寻找关联图片...")
                self.browser.scroll_to_load_more(1, 1)
                new_related_pins = self.browser.get_related_pins_from_current_page()
                
                if new_related_pins:
                    logger.info(f"  └─ 发现 {len(new_related_pins)} 个关联Pin")
                    
                    # === 关键改进：保存当前候选到历史池 ===
                    # 在进入新页面之前，把当前页面的其他候选保存起来
                    if current_source == "related":
                        # 如果当前是从关联池来的，把关联池剩下的保存到历史池
                        remaining_related = [p for p in related_pool if p.get('url') and p.get('url') not in visited_urls and p.get('url') != target_url]
                        if remaining_related:
                            history_pool.extend(remaining_related)
                            logger.info(f"  └─ 💾 保存 {len(remaining_related)} 个候选到历史池")
                    elif current_source == "search":
                        # 如果当前是从搜索池来的，把搜索池剩下的保存到历史池
                        remaining_main = [p for p in main_pool if p.get('url') and p.get('url') not in visited_urls and p.get('url') != target_url]
                        if remaining_main:
                            history_pool.extend(remaining_main)
                            logger.info(f"  └─ 💾 保存 {len(remaining_main)} 个候选到历史池")
                    
                    # 更新关联池为新发现的关联Pin
                    related_pool = new_related_pins
                else:
                    logger.info("  └─ ⚠️ 此处是死胡同(无关联图)")
                    # 不清空关联池，只是标记为当前无关联
                    # 下次循环会自动从历史池或主池选择
                    related_pool = []
                
                # 随机延迟
                self.browser.random_delay(1.5, 3.0)
            
            # 任务结束处理
            if recorded_count > 0:
                logger.info(f"✓ 处理完成：共记录 {recorded_count} 条信息")
                if self.sheets_exporter:
                    sheet_url = self.sheets_exporter.get_worksheet_url()
                    if sheet_url:
                        logger.info(f"✓ Google Sheets工作表URL: {sheet_url}")
            
            elapsed_time = time.time() - start_time
            return {
                'total_pins': 0,
                'recorded_count': recorded_count,
                'elapsed_time': elapsed_time,
                'sheet_url': self.sheets_exporter.get_worksheet_url() if self.sheets_exporter else None
            }
        
        except KeyboardInterrupt:
            logger.warning("⚠️  用户中断任务")
            return {}
        except Exception as e:
            logger.error(f"任务执行失败: {e}")
            raise
        finally:
            self.browser.close()
            self.is_running = False
    
    def stop(self):
        """停止下载任务"""
        if self.is_running:
            logger.info("正在停止任务...")
            self.should_stop = True


def main():
    """主函数"""
    print("=" * 60)
    print("Pinterest 高赞图片查找器 v2.0 (Google Sheets版)")
    print("=" * 60)
    print()
    print("⚠️  重要声明:")
    print("本工具仅供个人学习和研究使用")
    print("请遵守 Pinterest 服务条款，尊重原创者版权")
    print("不得用于商业目的或侵犯他人权益")
    print()
    
    try:
        # 加载配置
        config_manager = ConfigManager("config.json")
        print(f"成功加载配置文件: config.json")
        
        if not config_manager.validate():
            print("❌ 配置文件验证失败")
            return
        
        print("配置验证通过")
        
        # 创建下载器实例
        downloader = PinterestDownloader("config.json")
        
        # 显示当前配置
        keywords = config_manager.get('search.keywords')
        min_likes = config_manager.get('search.min_likes')
        max_results = config_manager.get('search.max_results')
        
        print(f"当前配置:")
        print(f"  搜索关键词: {keywords}")
        print(f"  最低点赞数: {min_likes}")
        print(f"  最大记录数: {max_results}")
        print(f"  输出方式: Google Sheets在线表格")
        print()
        
        # 确认开始
        response = input("是否开始任务？(y/n): ")
        if response.lower() != 'y':
            print("已取消")
            return
        
        print("\n开始任务...\n")
        
        # 开始任务
        stats = downloader.start()
        
        # 显示结果
        if stats:
            print("\n" + "=" * 60)
            print("任务完成！")
            print(f"找到 Pin: {stats.get('total_pins', 0)} 个")
            print(f"已记录: {stats.get('recorded_count', 0)} 条")
            print(f"总耗时: {stats.get('elapsed_time', 0):.2f} 秒")
            if stats.get('sheet_url'):
                print(f"查看结果: {stats.get('sheet_url')}")
            print("=" * 60)
    
    except KeyboardInterrupt:
        print("\n\n用户中断程序")
    except Exception as e:
        print(f"\n❌ 程序执行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
