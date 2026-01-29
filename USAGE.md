# 使用说明

## 快速开始

### 1. 安装依赖

首先确保已安装 Node.js，然后安装 agent-browser:

```bash
npm install -g agent-browser
```

安装 Python 依赖:

```bash
pip install -r requirements.txt
```

### 2. 运行程序

#### 命令行版本:

```bash
python run.py
```

#### GUI 版本（推荐）:

```bash
python run_gui.py
```

## 配置说明

编辑 `config.json` 文件来自定义参数：

- **search.keywords**: 搜索关键词
- **search.min_likes**: 最低点赞数（筛选条件）
- **search.max_results**: 最大下载数量
- **download.save_path**: 图片保存路径

## 注意事项  

### ⚠️ 重要提示

**当前版本状态**: Beta 测试版

由于 agent-browser 返回的页面快照格式需要根据实际 Pinterest 页面结构进行调整，完整的图片提取和下载功能需要进一步开发。

**当前已实现的功能**:
- ✅ 项目框架搭建
- ✅ 配置管理系统
- ✅ 日志记录系统
- ✅ 浏览器控制（搜索页面打开、滚动加载）
- ✅ 页面快照获取
- ✅ 图片下载模块
- ✅ GUI 界面

**待完善的功能**:
- ⏳ Pin 详情信息提取（需要根据实际快照格式调整）
- ⏳ 图片 URL 获取（需要根据实际页面结构调整）
- ⏳ 批量下载逻辑优化

### 🔧 调试模式

首次运行时，程序会将页面快照保存到 `debug_snapshot.txt` 文件，用于分析和调整提取逻辑。

### 📝 法律声明

- 本工具仅供个人学习和研究使用
- 请遵守 Pinterest 服务条款
- 尊重原创者版权
- 不得用于商业目的

## 故障排除

### agent-browser 未安装

如果提示 "agent-browser 未安装"，请运行:

```bash
npm install -g agent-browser
```

### 无法获取页面快照

1. 检查网络连接
2. 查看 `debug_snapshot.txt` 文件内容
3. 可能需要手动登录 Pinterest（当前版本不支持自动登录）

### 下载失败

1. 检查保存路径是否存在且有写入权限
2. 查看日志文件了解详细错误信息
3. 尝试降低下载数量或调整延迟时间

## 开发者信息

如需进一步开发或定制，请参考源代码注释和产品设计文档。

## 下一步计划

1. 根据实际 Pinterest 页面快照调整提取逻辑
2. 实现完整的图片 URL 获取功能
3. 优化下载性能和稳定性
4. 添加更多配置选项
5. 支持登录状态保持
