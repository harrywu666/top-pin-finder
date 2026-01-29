# 快速安装和测试指南

## 🚀 快速开始（5分钟）

### 步骤 1: 安装 Node.js（如果尚未安装）

访问 [nodejs.org](https://nodejs.org/) 下载并安装 LTS 版本。

### 步骤 2: 安装 agent-browser

打开命令行（PowerShell 或 CMD），运行：

```powershell
npm install -g agent-browser
```

### 步骤 3: 安装 Python 依赖

在项目目录下运行：

```powershell
cd d:\@dev\top-pin-finder
pip install -r requirements.txt
```

### 步骤 4: 运行程序

#### 选项 A: GUI 版本（推荐新手）

```powershell
python run_gui.py
```

#### 选项 B: 命令行版本

```powershell
python run.py
```

---

## ⚙️ 首次测试建议

### 测试配置

建议首次使用以下保守配置进行测试：

```json
{
  "search": {
    "keywords": "UI design",
    "min_likes": 100,
    "max_results": 10
  }
}
```

**原因**:
- 小数量下载便于快速测试
- 较低的点赞数阈值容易匹配到结果
- 英文关键词通用性更好

### 预期结果

程序运行后会：
1. ✅ 打开 Pinterest 搜索页面
2. ✅ 自动滚动加载内容
3. ✅ 保存页面快照到 `debug_snapshot.txt`
4. ⚠️ 可能无法自动提取 Pin 信息（需手动调整）

---

## 🔍 调试步骤

### 如果无法提取 Pin 信息

1. **查看快照文件**
   ```powershell
   notepad debug_snapshot.txt
   ```

2. **分析快照结构**  
   找到包含以下信息的元素：
   - 图片链接/标识
   - 点赞数文本
   - Pin 标题

3. **调整提取逻辑**  
   编辑 `src\core\browser_controller.py` 中的 `extract_pin_info()` 方法。

   示例调整：
   ```python
   def extract_pin_info(self, snapshot: str) -> List[Dict[str, any]]:
       # 根据实际快照格式调整这里的逻辑
       # 例如：
       # - 查找特定的元素标签
       # - 调整正则表达式
       # - 添加更多解析规则
       pass
   ```

---

## 🛠️ 常见问题

### Q1: 提示"agent-browser 未安装"

**解决方案**:
```powershell
npm install -g agent-browser
# 如果权限不足，以管理员身份运行 PowerShell
```

### Q2: 提示找不到模块

**解决方案**:
```powershell
pip install -r requirements.txt
# 确保使用正确的 Python 环境
```

### Q3: GUI 界面无法打开

**解决方案**:
```powershell
pip install PySide6
```

### Q4: 网络连接问题

**可能原因**:
- Pinterest 网站访问受限
- 需要科学上网工具

**解决方案**:
- 确保网络可以访问 Pinterest
- 配置代理（未来版本支持）

---

## 📋 测试检查清单

使用此清单验证安装是否成功：

- [ ] Node.js 已安装（`node --version`）
- [ ] agent-browser 已安装（`agent-browser --version`）
- [ ] Python 依赖已安装（`pip list | findstr requests`）
- [ ] PySide6 已安装（`pip list | findstr PySide6`）
- [ ] 可以运行 GUI 程序（`python run_gui.py`）
- [ ] 配置文件存在（`config.json`）
- [ ] 下载目录可创建（检查权限）

---

## 🎯 下一步行动

### 如果测试成功
1. 根据需要调整配置参数
2. 增加下载数量进行批量测试
3. 根据 `debug_snapshot.txt` 优化提取逻辑

### 如果遇到问题
1. 查看日志文件 `pinterest_downloader.log`
2. 参考 `USAGE.md` 中的故障排除章节
3. 检查 `debug_snapshot.txt` 了解页面结构

---

## 💡 提示

- **首次运行时间**: 可能需要 1-2 分钟加载页面
- **快照文件**: 每次运行都会生成，用于调试
- **日志文件**: 记录详细操作过程，有助于排查问题
- **保存路径**: 确保有足够磁盘空间

---

**祝使用愉快！** 🎉

如有问题，请查看项目文档或联系开发者。
