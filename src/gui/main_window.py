"""
GUI 主窗口
基于 PySide6 的图形用户界面
"""

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QSpinBox, QFileDialog,
    QProgressBar, QGroupBox, QMessageBox
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.main import PinterestDownloader
from src.utils.helpers import format_number


class DownloadThread(QThread):
    """下载线程，避免阻塞UI"""
    
    progress_update = Signal(dict)
    finished = Signal(dict)
    error = Signal(str)
    
    def __init__(self, downloader):
        super().__init__()
        self.downloader = downloader
    
    def run(self):
        """执行下载任务"""
        try:
            stats = self.downloader.start()
            self.finished.emit(stats)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.downloader = None
        self.download_thread = None
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("Pinterest 高赞图片下载器 v1.0")
        self.setMinimumSize(800, 600)
        
        # 创建中央Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title = QLabel("Pinterest 高赞图片下载器")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # 警告声明
        warning = QLabel("⚠️ 仅供个人学习使用 | 请遵守 Pinterest 服务条款 | 尊重原创者版权")
        warning.setStyleSheet("color: #d32f2f; background-color: #ffebee; padding: 10px; border-radius: 5px;")
        warning.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(warning)
        
        # 配置部分
        config_group = QGroupBox("下载配置")
        config_layout = QVBoxLayout()
        
        # 搜索关键词
        keyword_layout = QHBoxLayout()
        keyword_layout.addWidget(QLabel("搜索关键词:"))
        self.keyword_input = QLineEdit("UI设计")
        self.keyword_input.setPlaceholderText("输入搜索关键词，例如：UI设计、建筑设计")
        keyword_layout.addWidget(self.keyword_input)
        config_layout.addLayout(keyword_layout)
        
        # 点赞数阈值
        likes_layout = QHBoxLayout()
        likes_layout.addWidget(QLabel("最低点赞数:"))
        self.likes_input = QSpinBox()
        self.likes_input.setRange(0, 999999)
        self.likes_input.setValue(500)
        self.likes_input.setSuffix(" 赞")
        likes_layout.addWidget(self.likes_input)
        likes_layout.addStretch()
        config_layout.addLayout(likes_layout)
        
        # 下载数量
        count_layout = QHBoxLayout()
        count_layout.addWidget(QLabel("最大下载数:"))
        self.count_input = QSpinBox()
        self.count_input.setRange(1, 1000)
        self.count_input.setValue(100)
        self.count_input.setSuffix(" 张")
        count_layout.addWidget(self.count_input)
        count_layout.addStretch()
        config_layout.addLayout(count_layout)
        
        # 保存路径
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("保存路径:"))
        self.path_input = QLineEdit("./downloads")
        path_layout.addWidget(self.path_input)
        self.path_button = QPushButton("浏览...")
        self.path_button.clicked.connect(self.select_directory)
        path_layout.addWidget(self.path_button)
        config_layout.addLayout(path_layout)
        
        config_group.setLayout(config_layout)
        main_layout.addWidget(config_group)
        
        # 进度部分
        progress_group = QGroupBox("下载进度")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("color: #666; padding: 5px;")
        progress_layout.addWidget(self.status_label)
        
        progress_group.setLayout(progress_layout)
        main_layout.addWidget(progress_group)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("开始下载")
        self.start_button.setMinimumHeight(40)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.start_button.clicked.connect(self.start_download)
        button_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("停止")
        self.stop_button.setMinimumHeight(40)
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.stop_button.clicked.connect(self.stop_download)
        button_layout.addWidget(self.stop_button)
        
        main_layout.addLayout(button_layout)
        
        # 日志区域
        log_group = QGroupBox("运行日志")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)
        
        # 添加初始日志
        self.add_log("程序已启动，请配置下载参数后点击\"开始下载\"")
    
    def select_directory(self):
        """选择保存目录"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "选择保存目录",
            self.path_input.text()
        )
        if directory:
            self.path_input.setText(directory)
    
    def start_download(self):
        """开始下载"""
        try:
            # 禁用开始按钮
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            
            # 更新配置
            from src.core.config_manager import ConfigManager
            config = ConfigManager()
            
            config.set('search.keywords', self.keyword_input.text())
            config.set('search.min_likes', self.likes_input.value())
            config.set('search.max_results', self.count_input.value())
            config.set('download.save_path', self.path_input.text())
            
            config.save_config()
            
            # 创建下载器
            self.add_log(f"开始搜索: {self.keyword_input.text()}")
            self.add_log(f"点赞数阈值: {format_number(self.likes_input.value())}")
            self.add_log(f"最大下载数: {format_number(self.count_input.value())}")
            
            self.downloader = PinterestDownloader()
            
            # 创建下载线程
            self.download_thread = DownloadThread(self.downloader)
            self.download_thread.finished.connect(self.on_download_finished)
            self.download_thread.error.connect(self.on_download_error)
            self.download_thread.start()
            
            self.status_label.setText("正在下载...")
            
        except Exception as e:
            self.add_log(f"❌ 错误: {e}")
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            QMessageBox.critical(self, "错误", f"启动失败: {e}")
    
    def stop_download(self):
        """停止下载"""
        if self.downloader:
            self.downloader.stop()
            self.add_log("正在停止...")
    
    def on_download_finished(self, stats):
        """下载完成回调"""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        total_found = stats.get('total_found', 0)
        total_downloaded = stats.get('total_downloaded', 0)
        elapsed_time = stats.get('elapsed_time', 0)
        
        self.progress_bar.setValue(100)
        self.status_label.setText("下载完成")
        
        self.add_log("="*50)
        self.add_log(f"✓ 下载完成！")
        self.add_log(f"找到 Pin: {total_found} 个")
        self.add_log(f"已下载: {total_downloaded} 张")
        self.add_log(f"总耗时: {elapsed_time:.2f} 秒")
        self.add_log("="*50)
        
        QMessageBox.information(
            self,
            "完成",
            f"下载完成！\n\n找到: {total_found} 个 Pin\n已下载: {total_downloaded} 张图片\n耗时: {elapsed_time:.2f} 秒"
        )
    
    def on_download_error(self, error_msg):
        """下载错误回调"""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText("下载失败")
        
        self.add_log(f"❌ 错误: {error_msg}")
        
        QMessageBox.critical(self, "错误", f"下载失败:\n{error_msg}")
    
    def add_log(self, message: str):
        """添加日志"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        
        # 自动滚动到底部
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


def main():
    """GUI 主程序入口"""
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
