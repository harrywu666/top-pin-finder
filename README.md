# Pinterest 高赞图片下载器 (Top Pin Finder)

一个基于 Python 的自动化工具，可以在 Pinterest 上搜索指定类目的图片，并下载点赞数超过设定阈值的高质量图片。

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
- 📥 批量下载图片到本地
- 🎨 友好的图形用户界面
- 📊 实时显示下载进度
- 🔧 灵活的配置选项
- 📝 详细的操作日志

## 技术栈

- **Python 3.9+**: 主要开发语言
- **agent-browser**: 浏览器自动化工具
- **PySide6**: GUI 框架
- **requests**: HTTP 请求库
- **Pillow**: 图片处理库

## 安装步骤

### 1. 安装 Node.js

agent-browser 需要 Node.js 环境，请访问 [nodejs.org](https://nodejs.org/) 下载并安装。

### 2. 安装 agent-browser

```bash
npm install -g agent-browser
```

### 3. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

## 快速开始

### 命令行版本

```bash
# 使用默认配置
python run.py

# 指定配置文件
python run.py --config custom_config.json
```

### GUI 版本

```bash
python run_gui.py
```

## 配置说明

编辑 `config.json` 文件来自定义参数：

```json
{
  "search": {
    "keywords": "UI设计",
    "min_likes": 500,
    "max_results": 100
  },
  "download": {
    "save_path": "./downloads",
    "naming_format": "{category}_{likes}_{index}"
  }
}
```

### 主要配置项

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `search.keywords` | 搜索关键词 | "UI设计" |
| `search.min_likes` | 最低点赞数 | 500 |
| `search.max_results` | 最大下载数量 | 100 |
| `download.save_path` | 保存路径 | "./downloads" |
| `behavior.random_delay_min` | 最小延迟(秒) | 1 |
| `behavior.random_delay_max` | 最大延迟(秒) | 3 |

## 使用示例

### 示例 1: 下载 UI 设计灵感

```json
{
  "search": {
    "keywords": "UI design inspiration",
    "min_likes": 1000,
    "max_results": 50
  }
}
```

### 示例 2: 下载室内设计图片

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
│   ├── gui/               # GUI 界面
│   └── utils/             # 工具函数
├── config.json            # 配置文件
├── requirements.txt       # Python 依赖
├── run.py                 # 命令行启动脚本
├── run_gui.py            # GUI 启动脚本
└── README.md             # 本文件
```

## 常见问题

### Q: 为什么无法搜索到结果？

A: 请检查：
1. 网络连接是否正常
2. agent-browser 是否正确安装
3. Pinterest 是否需要登录

### Q: 如何避免被封禁？

A: 建议：
1. 增加随机延迟时间
2. 减少单次下载数量
3. 使用代理 IP（可选）
4. 不要频繁运行

### Q: 下载的图片质量如何？

A: 工具会尝试下载原始质量的图片，但受 Pinterest 限制可能获得压缩版本。

## 开发计划

- [x] 可行性研究
- [x] 产品设计文档
- [ ] 核心功能开发
- [ ] GUI 界面开发
- [ ] 测试与优化
- [ ] 发布 v1.0

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 免责声明

本工具仅供学习和研究使用。用户应自行承担使用本工具的所有风险和责任。开发者不对因使用本工具而产生的任何直接或间接损失承担责任。
