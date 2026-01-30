# Pinterest 高赞图片下载器 (Top Pin Finder)

一个基于 Python 的自动化工具，可以在 Pinterest 上搜索指定类目的图片，并记录点赞数超过设定阈值的高质量图片到 Google Sheets。

## ⚠️ 重要声明

本工具仅供个人学习和研究使用。使用本工具时请注意：

1. 遵守 Pinterest 服务条款
2. 尊重原创者版权
3. 不得用于商业目的
4. 下载的图片仅供个人学习和设计参考
5. 控制爬取频率，避免对 Pinterest 服务器造成负担

**开发者不对用户的不当使用承担责任。**

## 功能特性

- ✨ 自动搜索指定关键词的 Pinterest 图片
- 🎯 根据点赞数筛选高质量图片
- 🎨 友好的图形用户界面 (GUI)
- 📊 实时显示搜索进度
- 🔧 灵活的配置选项
- 📝 详细的操作日志
- 📤 **Google Sheets 实时同步** - 符合条件的图片自动记录到在线表格
- 🔀 **多种排序方式** - 支持按相关性、最新、热门排序
- 💾 **智能去重** - 自动记录已处理的 Pin，避免重复
- 🚶 **随机漫步模式** - 模拟真人浏览行为，降低被封风险

## 技术栈

- **Python 3.9+**: 主要开发语言
- **Playwright**: 浏览器自动化工具
- **PySide6**: GUI 框架
- **gspread**: Google Sheets API 集成
- **openpyxl**: Excel 导出支持

## 安装步骤

### 1. 安装 Node.js

Playwright 需要 Node.js 环境，请访问 [nodejs.org](https://nodejs.org/) 下载并安装。

### 2. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 3. 安装 Playwright 浏览器

```bash
playwright install chromium
```

### 4. 配置 Google Sheets (可选)

如需使用 Google Sheets 同步功能：

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建项目并启用 Google Sheets API
3. 创建服务账号并下载 `credentials.json`
4. 将凭证文件放在项目根目录
5. 在 `config.json` 中配置 `google_sheets.spreadsheet_id`

## 快速开始

### GUI 版本（推荐）

```bash
python run_gui.py
```

### 命令行版本

```bash
# 使用默认配置
python run.py

# 指定配置文件
python run.py --config custom_config.json
```

## 配置说明

编辑 `config.json` 文件来自定义参数：

```json
{
  "pinterest": {
    "login_required": false,
    "session_cookie": ""
  },
  "search": {
    "keywords": "壁纸",
    "min_likes": 100,
    "max_results": 5,
    "sort_by": "relevance",
    "enable_random": true,
    "random_sort_probability": 0.8,
    "history_file": "./downloads/.download_history.json"
  },
  "download": {
    "save_path": "./downloads",
    "naming_format": "{category}_{likes}_{index}",
    "excel_auto_save": true,
    "enable_local_download": false
  },
  "google_sheets": {
    "enabled": true,
    "spreadsheet_id": "your_spreadsheet_id",
    "credentials_file": "./credentials.json"
  },
  "behavior": {
    "random_delay_min": 1,
    "random_delay_max": 3
  },
  "logging": {
    "level": "INFO",
    "file": "pinterest_downloader.log"
  }
}
```

### 主要配置项

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `search.keywords` | 搜索关键词 | "壁纸" |
| `search.min_likes` | 最低点赞数 | 100 |
| `search.max_results` | 最大记录数量 | 5 |
| `search.sort_by` | 排序方式 (relevance/latest/popular) | "relevance" |
| `search.enable_random` | 启用随机化排序 | true |
| `search.history_file` | 历史记录文件路径 | "./downloads/.download_history.json" |
| `download.save_path` | 保存路径 | "./downloads" |
| `download.excel_auto_save` | Excel 实时保存 | true |
| `download.enable_local_download` | 启用本地图片下载 | false |
| `google_sheets.enabled` | 启用 Google Sheets 同步 | true |
| `google_sheets.spreadsheet_id` | Google 表格 ID | "" |
| `behavior.random_delay_min` | 最小延迟(秒) | 1 |
| `behavior.random_delay_max` | 最大延迟(秒) | 3 |

## 使用示例

### 示例 1: 搜索 UI 设计灵感

```json
{
  "search": {
    "keywords": "UI design inspiration",
    "min_likes": 1000,
    "max_results": 50
  }
}
```

### 示例 2: 搜索室内设计图片

```json
{
  "search": {
    "keywords": "modern interior design",
    "min_likes": 500,
    "max_results": 100
  }
}
```

## 项目结构

```
top-pin-finder/
├── src/
│   ├── core/              # 核心业务逻辑
│   │   ├── browser_controller.py   # 浏览器控制
│   │   ├── config_manager.py       # 配置管理
│   │   ├── downloader.py           # 下载器
│   │   └── logger.py               # 日志记录
│   ├── gui/               # GUI 界面
│   │   └── main_window.py          # 主窗口
│   ├── utils/             # 工具函数
│   │   ├── excel_exporter.py       # Excel 导出
│   │   ├── google_sheets_exporter.py  # Google Sheets 导出
│   │   ├── history_manager.py      # 历史记录管理
│   │   └── helpers.py              # 辅助函数
│   ├── main.py            # 主控制器
│   ├── __init__.py
├── config.json            # 配置文件
├── requirements.txt       # Python 依赖
├── run.py                 # 命令行启动脚本
├── run_gui.py             # GUI 启动脚本
├── README.md              # 本文件
├── USAGE.md               # 使用说明
├── INSTALL.md             # 安装指南
└── .trae/documents/       # 开发文档
```

## 随机漫步算法

本工具采用独特的"随机漫步"模式模拟真人浏览行为：

1. **初始搜索** - 打开 Pinterest 搜索页面
2. **候选池管理** - 维护主池、关联池、历史池三个候选队列
3. **智能选择** - 优先从关联推荐选择，模拟深度浏览
4. **回退机制** - 关联池耗尽时从历史池回退
5. **重新加载** - 所有池耗尽时滚动加载更多内容

这种模式可以有效降低被 Pinterest 检测为机器人的风险。

## 常见问题

### Q: 为什么无法搜索到结果？

A: 请检查：
1. 网络连接是否正常
2. Playwright 浏览器是否正确安装
3. Pinterest 是否需要登录（可在配置中设置）

### Q: 如何避免被封禁？

A: 建议：
1. 增加随机延迟时间 (`random_delay_min/max`)
2. 减少单次记录数量 (`max_results`)
3. 启用随机化排序 (`enable_random: true`)
4. 不要频繁运行

### Q: Google Sheets 同步失败？

A: 请检查：
1. `credentials.json` 文件是否存在且有效
2. Google Sheets API 是否已启用
3. 服务账号是否有权限访问目标表格
4. `spreadsheet_id` 是否正确

## 开发计划

- [x] 可行性研究
- [x] 核心功能开发
- [x] GUI 界面开发
- [x] Google Sheets 集成
- [x] 随机漫步算法
- [ ] 飞书表格集成 (计划中)
- [ ] 代理 IP 支持 (计划中)
- [ ] 自动登录功能 (计划中)

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 免责声明

本工具仅供学习和研究使用。用户应自行承担使用本工具的所有风险和责任。开发者不对因使用本工具而产生的任何直接或间接损失承担责任。
