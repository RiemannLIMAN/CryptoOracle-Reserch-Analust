# 📜 脚本使用手册 (Script Usage Guide)

本文档详细介绍了如何使用项目提供的一键启动脚本来运行 OKX Research Analyst。

我们为 Windows 和 Linux/Mac 用户分别提供了专用的启动脚本，这些脚本会自动处理虚拟环境创建、依赖安装和程序启动，让您**零门槛**上手。

---

## 1. 🪟 Windows 用户 (`run.bat`)

`run.bat` 是 Windows 平台下的批处理启动脚本。

### 1.1 基本用法
双击 `run.bat` 或在 CMD/PowerShell 中运行：
```powershell
.\run.bat
```
*   **首次运行**: 脚本会自动创建一个名为 `okx_research` (或 `.env` 中配置的名字) 的虚拟环境，并安装所有依赖。
*   **日常运行**: 脚本会自动激活环境并启动分析程序。

### 1.2 传递自定义分析指令
您可以在脚本后直接跟上您想问 AI 的问题：
```powershell
.\run.bat "帮我分析一下里面的 Meme 币有哪些风险，重点看 PEPE"
```

### 1.3 后台静默运行 (守护模式)
如果您开启了定时任务 (`ENABLE_SCHEDULER=true`)，并希望程序在后台运行不占用当前窗口：
```powershell
.\run.bat -d
```
或者：
```powershell
.\run.bat --daemon
```
*   程序将启动一个新的**最小化窗口**运行。
*   您可以随时关闭该最小化窗口来停止程序。
*   日志会记录在 `logs/okx_research.log`。

---

## 2. 🐧 Linux / 🍎 Mac 用户 (`run.sh`)

`run.sh` 是适用于 Unix-like 系统的 Shell 脚本。

### 2.1 赋予执行权限 (首次)
在使用前，请确保脚本有执行权限：
```bash
chmod +x run.sh
```

### 2.2 基本用法
```bash
./run.sh
```
*   脚本会自动检查 Python3 环境。
*   自动创建并激活虚拟环境。
*   安装依赖并启动程序。

### 2.3 传递自定义分析指令
```bash
./run.sh "请分析 Layer2 板块的投资机会"
```

### 2.4 后台静默运行 (守护模式)
适用于服务器部署或长期运行：
```bash
./run.sh -d
```
或者：
```bash
./run.sh --daemon
```
*   程序将使用 `nohup` 在后台运行。
*   启动后会显示进程 PID。
*   **停止程序**: 使用 `kill <PID>` 命令。
*   **查看日志**: 标准输出日志会重定向到 `logs/nohup.log`，业务日志在 `logs/okx_research.log`。

#### 🕵️ 如何确认运行状态？
**方法 1: 查看进程**
```bash
# 检查 main.py 是否在运行
ps -ef | grep main.py
```

**方法 2: 实时查看日志**
这是最直观的方法，可以看到程序正在干什么：
```bash
# 查看启动输出（如果有报错会显示在这里）
tail -f logs/nohup.log

# 查看业务日志（分析进度、结果等）
tail -f logs/okx_research.log
```

---

## 3. 🐍 纯 Python 方式运行

如果您更喜欢手动管理环境，可以直接调用 Python 脚本。

### 3.1 前置条件
确保您已经激活了虚拟环境并安装了依赖：
```bash
# 激活环境
source okx_research/bin/activate  # Linux/Mac
okx_research\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 3.2 运行命令
```bash
# 默认分析
python src/main.py

# 带指令分析
python src/main.py "分析 AI 板块龙头的走势"
```

---

## 4. ❓ 常见问题 (Troubleshooting)

### Q1: 脚本提示 "Python is not installed"
*   **原因**: 系统 PATH 环境变量中找不到 `python` (Windows) 或 `python3` (Linux/Mac) 命令。
*   **解决**: 请安装 Python 3.8+，并在安装时勾选 "Add Python to PATH"。

### Q2: 依赖安装失败 (pip install error)
*   **原因**: 网络问题或缺少编译工具。
*   **解决**: 尝试更换国内 pip 源，例如：
    ```bash
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    ```

### Q3: 修改了 `.env` 但没生效
*   **原因**: 程序启动时才会读取 `.env`。
*   **解决**: 请关闭当前运行的程序（Ctrl+C），然后重新运行脚本。

### Q4: 想要修改虚拟环境的名字
*   **解决**: 在 `.env` 文件中添加一行：
    ```ini
    VENV_NAME=my_custom_env
    ```
    脚本下次运行时会识别并使用这个新环境。
