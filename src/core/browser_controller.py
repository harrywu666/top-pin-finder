"""
浏览器控制模块
使用 Playwright 控制浏览器进行自动化操作
"""

import time
import random
import re
from typing import List, Dict, Optional
from playwright.sync_api import sync_playwright, Page, Browser
try:
    from playwright_stealth import stealth_sync
    _stealth_available = True
except ImportError:
    _stealth_available = False
from .logger import logger


class BrowserController:
    """使用 Playwright 控制浏览器"""
    
    def __init__(self, headless: bool = True):
        """
        初始化浏览器控制器
        
        Args:
            headless: 是否使用无头模式（默认True，后台运行）
        """
        self.headless = headless
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.session_active = False
        logger.info(f"浏览器控制器已初始化 (headless={headless})")
    
    def start_browser(self):
        """启动浏览器"""
        try:
            if not self.playwright:
                logger.info("启动Playwright浏览器...")
                self.playwright = sync_playwright().start()
                
                # 启动Chromium浏览器
                self.browser = self.playwright.chromium.launch(
                    headless=self.headless,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                    ]
                )
                
                # 创建新页面
                self.page = self.browser.new_page(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                
                # 应用隐身模式（如果可用）
                if _stealth_available:
                    try:
                        stealth_sync(self.page)
                        logger.debug("已应用隐身模式")
                    except Exception as e:
                        logger.warning(f"应用隐身模式失败: {e}")
                
                self.session_active = True
                logger.info("✓ Playwright浏览器已启动")
                
        except Exception as e:
            logger.error(f"启动浏览器失败: {e}")
            raise
    
    def check_playwright_installed(self) -> bool:
        """
        检查 Playwright 是否已安装
        
        Returns:
            是否已安装
        """
        try:
            import playwright
            logger.info("✓ Playwright 已安装")
            return True
        except ImportError:
            logger.error("✗ Playwright 未安装，请运行: pip install playwright && playwright install chromium")
            return False
    
    def open_pinterest_search(self, keyword: str) -> bool:
        """
        打开 Pinterest 搜索页面
        
        Args:
            keyword: 搜索关键词
        
        Returns:
            是否成功
        """
        try:
            # 如果浏览器未启动，先启动
            if not self.session_active:
                self.start_browser()
            
            # URL编码关键词
            import urllib.parse
            encoded_keyword = urllib.parse.quote(keyword)
            url = f"https://www.pinterest.com/search/pins/?q={encoded_keyword}"
            
            logger.info(f"打开搜索页面: {keyword}")
            
            # 访问页面，等待网络空闲
            self.page.goto(url, wait_until='networkidle', timeout=30000)
            
            # 额外等待确保动态内容加载
            time.sleep(3)
            
            logger.info("✓ 搜索页面已打开")
            return True
            
        except Exception as e:
            logger.error(f"打开搜索页面失败: {e}")
            return False
    
    def scroll_to_load_more(self, scroll_times: int = 3, delay: float = 2.0):
        """
        滚动页面加载更多内容
        
        Args:
            scroll_times: 滚动次数
            delay: 每次滚动后的延迟（秒）
        """
        try:
            logger.info(f"开始滚动加载，共 {scroll_times} 次")
            
            for i in range(scroll_times):
                # 滚动页面
                self.page.evaluate("window.scrollBy(0, 1000)")
                
                # 随机延迟，模拟人类行为
                wait_time = delay + random.uniform(-0.5, 0.5)
                time.sleep(wait_time)
                
                logger.debug(f"第 {i+1}/{scroll_times} 次滚动完成")
            
            # 等待新内容加载
            time.sleep(2)
            
            logger.info("✓ 滚动加载完成")
        except Exception as e:
            logger.error(f"滚动加载失败: {e}")
    
    def get_snapshot(self) -> str:
        """
        获取当前页面的HTML内容
        
        Returns:
            页面HTML
        """
        try:
            logger.debug("获取页面内容")
            
            if not self.page:
                logger.error("页面未初始化")
                return ""
            
            # 获取页面HTML
            html_content = self.page.content()
            
            logger.info(f"✓ 获取页面内容成功 (长度: {len(html_content)} 字符)")
            return html_content
            
        except Exception as e:
            logger.error(f"获取页面内容失败: {e}")
            return ""
    
    def extract_likes_from_detail_page(self, pin_url: str) -> int:
        """
        从Pin详情页提取精确的点赞数
        
        Args:
            pin_url: Pin详情页URL
        
        Returns:
            点赞数（整数）
        """
        try:
            if not self.page:
                logger.error("Page对象不存在")
                return 0
            
            # 在新标签页打开详情页
            detail_page = self.browser.new_page()
            
            try:
                # 访问详情页，设置超时5秒
                detail_page.goto(pin_url, timeout=5000, wait_until='domcontentloaded')
                
                # 等待页面稳定（等待可能的动态加载）
                detail_page.wait_for_timeout(1000)
                
                # 使用JavaScript提取点赞数
                likes = detail_page.evaluate("""
                    () => {
                        // 获取页面所有文本
                        const allText = document.body.innerText || '';
                        const lines = allText.split('\\n');
                        
                        let maxLikes = 0;
                        
                        // 查找纯数字或带K/M/B后缀的文本
                        for (const line of lines) {
                            const trimmed = line.trim();
                            const cleaned = trimmed.replace(/,/g, '');
                            const match = cleaned.match(/^(\\d+\\.?\\d*[KMB]?)$/);
                            
                            if (match) {
                                const numStr = match[1];
                                let num = parseFloat(numStr);
                                if (numStr.includes('K')) num *= 1000;
                                else if (numStr.includes('M')) num *= 1000000;
                                else if (numStr.includes('B')) num *= 1000000000;
                                
                                // 点赞数通常在10-1000万之间，取最大的一个
                                if (num >= 10 && num < 10000000 && num > maxLikes) {
                                    maxLikes = Math.floor(num);
                                }
                            }
                        }
                        
                        return maxLikes;
                    }
                """)
                
                return likes if likes else 0
                
            finally:
                # 确保关闭详情页标签
                detail_page.close()
                
        except Exception as e:
            logger.debug(f"从详情页提取点赞数失败 ({pin_url}): {e}")
            return 0
    
    def extract_pin_basic_info(self) -> List[Dict]:
        """
        从搜索结果页提取Pin的基本信息（URL和图片链接）
        
        不提取点赞数，点赞数将在后续访问详情页时单独获取
        
        Returns:
            Pin 基本信息列表
        """
        pins = []
        
        try:
            if not self.page:
                logger.error("Page对象不存在")
                return []
            
            logger.info("从搜索结果页提取Pin基本信息...")
            
            # 使用JavaScript从页面中提取所有Pin的基本信息
            pins_data = self.page.evaluate("""
                () => {
                    const pins = [];
                    const pinElements = document.querySelectorAll('[data-test-id="pin"]');
                    
                    pinElements.forEach((pinEl, index) => {
                        try {
                            const pinData = {};
                            
                            // 提取Pin链接
                            const link = pinEl.querySelector('a[href*="/pin/"]');
                            if (link) {
                                pinData.url = link.href;
                                const pinIdMatch = link.href.match(/\\/pin\\/(\\d+)/);
                                if (pinIdMatch) {
                                    pinData.pin_id = pinIdMatch[1];
                                }
                            }
                            
                            // 提取图片URL
                            const img = pinEl.querySelector('img');
                            if (img) {
                                pinData.image_url = img.src || img.dataset.src;
                                pinData.title = img.alt || '';
                                
                                // 转换为高质量图片URL
                                if (pinData.image_url) {
                                    if (pinData.image_url.includes('/236x/')) {
                                        pinData.image_url_hq = pinData.image_url.replace('/236x/', '/originals/');
                                    } else if (pinData.image_url.includes('/474x/')) {
                                        pinData.image_url_hq = pinData.image_url.replace('/474x/', '/originals/');
                                    } else if (pinData.image_url.includes('/736x/')) {
                                        pinData.image_url_hq = pinData.image_url.replace('/736x/', '/originals/');
                                    }
                                }
                            }
                            
                            // 只添加有图片URL和Pin URL的Pin
                            if (pinData.image_url && pinData.url) {
                                pins.push(pinData);
                            }
                        } catch (e) {
                            console.error('提取单个Pin失败:', e);
                        }
                    });
                    
                    return pins;
                }
            """)
            
            logger.info(f"✓ 从搜索结果页提取到 {len(pins_data)} 个 Pin")
            
            # 去重
            seen_urls = set()
            for pin in pins_data:
                if pin.get('image_url') not in seen_urls:
                    seen_urls.add(pin.get('image_url'))
                    pins.append(pin)
            
            logger.info(f"✓ 去重后剩余 {len(pins)} 个唯一的 Pin")
            
            return pins
            
        except Exception as e:
            logger.error(f"提取 Pin 基本信息失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _parse_likes_count(self, likes_str: str) -> int:
        """
        解析点赞数字符串
        
        Args:
            likes_str: 点赞数字符串，如 "1.2K", "523"
        
        Returns:
            点赞数整数
        """
        try:
            likes_str = likes_str.strip().upper()
            
            if 'K' in likes_str:
                return int(float(likes_str.replace('K', '')) * 1000)
            elif 'M' in likes_str:
                return int(float(likes_str.replace('M', '')) * 1000000)
            elif 'B' in likes_str:
                return int(float(likes_str.replace('B', '')) * 1000000000)
            else:
                return int(likes_str)
        except Exception:
            return 0
    
    def click_element(self, selector: str) -> bool:
        """
        点击指定元素
        
        Args:
            selector: CSS选择器
        
        Returns:
            是否成功
        """
        try:
            logger.debug(f"点击元素: {selector}")
            self.page.click(selector, timeout=5000)
            return True
        except Exception as e:
            logger.error(f"点击元素失败: {e}")
            return False
    
    def screenshot(self, filename: str = "screenshot.png") -> bool:
        """
        截取当前页面截图
        
        Args:
            filename: 截图文件名
        
        Returns:
            是否成功
        """
        try:
            logger.info(f"截图保存到: {filename}")
            self.page.screenshot(path=filename, full_page=True)
            return True
        except Exception as e:
            logger.error(f"截图失败: {e}")
            return False
    
    def close(self):
        """关闭浏览器"""
        try:
            if self.session_active:
                logger.info("关闭浏览器")
                
                if self.page:
                    self.page.close()
                    self.page = None
                
                if self.browser:
                    self.browser.close()
                    self.browser = None
                
                if self.playwright:
                    self.playwright.stop()
                    self.playwright = None
                
                self.session_active = False
                logger.info("✓ 浏览器已关闭")
                
        except Exception as e:
            logger.error(f"关闭浏览器失败: {e}")
    
    def random_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """
        随机延迟，模拟人类行为
        
        Args:
            min_seconds: 最小延迟秒数
            max_seconds: 最大延迟秒数
        """
        delay = random.uniform(min_seconds, max_seconds)
        logger.debug(f"随机延迟 {delay:.2f} 秒")
        time.sleep(delay)


if __name__ == "__main__":
    # 测试浏览器控制器
    browser = BrowserController()
    
    # 检查安装
    if not browser.check_playwright_installed():
        print("请先安装 Playwright: pip install playwright && playwright install chromium")
    else:
        # 测试搜索
        browser.open_pinterest_search("UI设计")
        browser.scroll_to_load_more(2)
        
        # 获取内容
        snapshot = browser.get_snapshot()
        print(f"\n页面内容长度: {len(snapshot)} 字符")
        
        # 提取Pin信息
        pins = browser.extract_pin_basic_info()
        print(f"提取到 {len(pins)} 个 Pin")
        
        if pins:
            print("\n示例Pin信息:")
            print(pins[0])
        
        # 截图
        browser.screenshot("test_screenshot.png")
        
        # 关闭
        browser.close()
