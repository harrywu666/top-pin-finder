"""
Google Sheets导出模块
负责将下载的图片信息导出到Google Sheets在线表格
"""

import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from typing import List, Dict, Optional
from ..core.logger import logger


class GoogleSheetsExporter:
    """Google Sheets导出器 - 将Pin信息写入在线表格"""
    
    def __init__(self, spreadsheet_id: str, credentials_file: str):
        """
        初始化Google Sheets导出器
        
        Args:
            spreadsheet_id: Google Sheets文档ID
            credentials_file: Service Account凭证JSON文件路径
        """
        self.spreadsheet_id = spreadsheet_id
        self.credentials_file = credentials_file
        self.client = None
        self.spreadsheet = None
        self.worksheet = None
        self.records = []  # 缓存记录,最后批量写入
        self.current_index = 0  # 当前序号
        
        logger.info(f"Google Sheets导出器已初始化")
    
    def connect(self):
        """连接到Google Sheets"""
        try:
            # 定义访问范围
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # 使用Service Account凭证认证
            creds = Credentials.from_service_account_file(
                self.credentials_file,
                scopes=scopes
            )
            
            # 创建gspread客户端
            self.client = gspread.authorize(creds)
            
            # 打开指定的Spreadsheet
            self.spreadsheet = self.client.open_by_key(self.spreadsheet_id)
            
            logger.info(f"✓ 已连接到Google Sheets: {self.spreadsheet.title}")
            return True
            
        except FileNotFoundError:
            logger.error(f"凭证文件不存在: {self.credentials_file}")
            logger.error("请将Google Service Account凭证JSON文件放置在项目根目录")
            return False
        except Exception as e:
            logger.error(f"连接Google Sheets失败: {e}")
            return False
    
    def create_worksheet(self, task_name: str) -> bool:
        """
        创建新工作表（三栏布局）
        
        Args:
            task_name: 任务名称,用于工作表标题
        
        Returns:
            是否成功创建
        """
        try:
            # 生成工作表名称(时间戳 + 任务名)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            sheet_title = f"{task_name}_{timestamp}"
            
            # 创建新工作表(12列:左栏4列 + 中栏4列 + 右栏4列)
            self.worksheet = self.spreadsheet.add_worksheet(
                title=sheet_title,
                rows=100,
                cols=12,
                index=0  # 关键:设置为0,将新工作表放在最左边
            )
            
            logger.info(f"✓ 已创建新工作表: {sheet_title} (位置:最左)")
            
            # 设置表头(三栏布局:左栏A-D,中栏E-H,右栏I-L)
            headers = [["序号", "图片预览", "点赞数", "Pin链接", "序号", "图片预览", "点赞数", "Pin链接", "序号", "图片预览", "点赞数", "Pin链接"]]
            self.worksheet.update('A1:L1', headers, value_input_option='RAW')
            
            # 格式化表头
            self.worksheet.format('A1:L1', {
                "backgroundColor": {"red": 0.27, "green": 0.45, "blue": 0.77},
                "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
                "horizontalAlignment": "CENTER"
            })
            
            # 启用筛选
            self.worksheet.set_basic_filter()
            
            # 设置各列宽度(三栏布局，每栏4列，更紧凑)
            column_width_requests = [
                # 左栏 A列(序号): 40像素
                {"updateDimensionProperties": {"range": {"sheetId": self.worksheet.id, "dimension": "COLUMNS", "startIndex": 0, "endIndex": 1}, "properties": {"pixelSize": 40}, "fields": "pixelSize"}},
                # 左栏 B列(图片预览): 120像素
                {"updateDimensionProperties": {"range": {"sheetId": self.worksheet.id, "dimension": "COLUMNS", "startIndex": 1, "endIndex": 2}, "properties": {"pixelSize": 120}, "fields": "pixelSize"}},
                # 左栏 C列(点赞数): 50像素
                {"updateDimensionProperties": {"range": {"sheetId": self.worksheet.id, "dimension": "COLUMNS", "startIndex": 2, "endIndex": 3}, "properties": {"pixelSize": 50}, "fields": "pixelSize"}},
                # 左栏 D列(Pin链接): 200像素
                {"updateDimensionProperties": {"range": {"sheetId": self.worksheet.id, "dimension": "COLUMNS", "startIndex": 3, "endIndex": 4}, "properties": {"pixelSize": 200}, "fields": "pixelSize"}},
                
                # 中栏 E列(序号): 40像素
                {"updateDimensionProperties": {"range": {"sheetId": self.worksheet.id, "dimension": "COLUMNS", "startIndex": 4, "endIndex": 5}, "properties": {"pixelSize": 40}, "fields": "pixelSize"}},
                # 中栏 F列(图片预览): 120像素
                {"updateDimensionProperties": {"range": {"sheetId": self.worksheet.id, "dimension": "COLUMNS", "startIndex": 5, "endIndex": 6}, "properties": {"pixelSize": 120}, "fields": "pixelSize"}},
                # 中栏 G列(点赞数): 50像素
                {"updateDimensionProperties": {"range": {"sheetId": self.worksheet.id, "dimension": "COLUMNS", "startIndex": 6, "endIndex": 7}, "properties": {"pixelSize": 50}, "fields": "pixelSize"}},
                # 中栏 H列(Pin链接): 200像素
                {"updateDimensionProperties": {"range": {"sheetId": self.worksheet.id, "dimension": "COLUMNS", "startIndex": 7, "endIndex": 8}, "properties": {"pixelSize": 200}, "fields": "pixelSize"}},
                
                # 右栏 I列(序号): 40像素
                {"updateDimensionProperties": {"range": {"sheetId": self.worksheet.id, "dimension": "COLUMNS", "startIndex": 8, "endIndex": 9}, "properties": {"pixelSize": 40}, "fields": "pixelSize"}},
                # 右栏 J列(图片预览): 120像素
                {"updateDimensionProperties": {"range": {"sheetId": self.worksheet.id, "dimension": "COLUMNS", "startIndex": 9, "endIndex": 10}, "properties": {"pixelSize": 120}, "fields": "pixelSize"}},
                # 右栏 K列(点赞数): 50像素
                {"updateDimensionProperties": {"range": {"sheetId": self.worksheet.id, "dimension": "COLUMNS", "startIndex": 10, "endIndex": 11}, "properties": {"pixelSize": 50}, "fields": "pixelSize"}},
                # 右栏 L列(Pin链接): 200像素
                {"updateDimensionProperties": {"range": {"sheetId": self.worksheet.id, "dimension": "COLUMNS", "startIndex": 11, "endIndex": 12}, "properties": {"pixelSize": 200}, "fields": "pixelSize"}}
            ]
            self.spreadsheet.batch_update({'requests': column_width_requests})
            
            logger.info("✓ 表头已设置,三栏布局已优化")
            return True
            
        except Exception as e:
            logger.error(f"创建工作表失败: {e}")
            return False
    
    def add_record(self, index: int, image_url: str, likes: int, title: str, pin_url: str):
        """
        实时添加一条记录到Google Sheets(三栏布局)
        
        Args:
            index: 序号
            image_url: 图片URL
            likes: 点赞数
            title: 标题(不使用)
            pin_url: Pin详情页URL
        """
        try:
            self.current_index += 1
            actual_index = self.current_index
            
            # 使用IMAGE函数在Google Sheets中显示图片
            image_formula = f'=IMAGE("{image_url}", 1)'
            
            # 判断是左栏、中栏还是右栏
            # 1,4,7...放左栏(A-D)，2,5,8...放中栏(E-H)，3,6,9...放右栏(I-L)
            remainder = actual_index % 3
            
            if remainder == 1:
                # 左栏: A-D列
                row_number = (actual_index + 2) // 3 + 1
                record = [actual_index, image_formula, likes, pin_url]
                range_name = f'A{row_number}:D{row_number}'
                col_offset = 0
                col_name = "左栏"
            elif remainder == 2:
                # 中栏: E-H列
                row_number = (actual_index + 1) // 3 + 1
                record = [actual_index, image_formula, likes, pin_url]
                range_name = f'E{row_number}:H{row_number}'
                col_offset = 4
                col_name = "中栏"
            else:
                # 右栏: I-L列 (remainder == 0)
                row_number = actual_index // 3 + 1
                record = [actual_index, image_formula, likes, pin_url]
                range_name = f'I{row_number}:L{row_number}'
                col_offset = 8
                col_name = "右栏"
            
            # 实时写入到Google Sheets
            self.worksheet.update(
                range_name,
                [record],
                value_input_option='USER_ENTERED'
            )
            
            # 设置行高和格式（包括自动换行）
            format_requests = []
            
            # 设置行高为140像素(三栏布局行高更紧凑)
            format_requests.append({
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": self.worksheet.id,
                        "dimension": "ROWS",
                        "startIndex": row_number - 1,
                        "endIndex": row_number
                    },
                    "properties": {"pixelSize": 140},
                    "fields": "pixelSize"
                }
            })
            
            # 当前行的4列设置格式
            for i in range(4):
                cell_format = {
                    "userEnteredFormat": {
                        "horizontalAlignment": "CENTER",
                        "verticalAlignment": "MIDDLE"
                    }
                }
                
                # Pin链接列(每栏第4列)添加自动换行
                if i == 3:
                    cell_format["userEnteredFormat"]["wrapStrategy"] = "WRAP"
                
                format_requests.append({
                    "repeatCell": {
                        "range": {
                            "sheetId": self.worksheet.id,
                            "startRowIndex": row_number - 1,
                            "endRowIndex": row_number,
                            "startColumnIndex": col_offset + i,
                            "endColumnIndex": col_offset + i + 1
                        },
                        "cell": cell_format,
                        "fields": "userEnteredFormat(horizontalAlignment,verticalAlignment,wrapStrategy)"
                    }
                })
            
            # 批量应用格式
            self.spreadsheet.batch_update({'requests': format_requests})
            
            logger.debug(f"✓ 已实时写入记录: Pin #{actual_index} ({col_name})")
            
        except Exception as e:
            logger.error(f"实时写入记录失败: {e}")
    
    def get_record_count(self) -> int:
        """获取记录数量"""
        return self.current_index
    
    def get_worksheet_url(self) -> Optional[str]:
        """获取当前工作表的URL"""
        if self.worksheet:
            return self.worksheet.url
        return None


if __name__ == "__main__":
    # 测试Google Sheets导出器
    SPREADSHEET_ID = "1XPVYEGgqpuCWEqmmeva8kMWIL52ClpIk52kXKVGmoHk"
    CREDENTIALS_FILE = "./credentials.json"
    
    exporter = GoogleSheetsExporter(SPREADSHEET_ID, CREDENTIALS_FILE)
    
    if exporter.connect():
        if exporter.create_worksheet("测试"):
            # 添加测试数据
            for i in range(1, 10):
                exporter.add_record(
                    index=i,
                    image_url=f"https://i.pinimg.com/originals/sample{i}.jpg",
                    likes=1000 + i,
                    title=f"测试图片{i}",
                    pin_url=f"https://www.pinterest.com/pin/123456{i}/"
                )
            
            print(f"✓ 测试完成,工作表URL: {exporter.get_worksheet_url()}")
