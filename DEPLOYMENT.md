# 🚀 Local-KB 部署指南

本指南提供了在新工作站上部署 **Local-KB** 系统的详细步骤。

---

## 📋 1. 系统要求

确保工作站满足以下配置：

*   **操作系统**: Windows 10/11, macOS, 或 Linux
*   **内存 (RAM)**: 建议至少 16GB (为了流畅运行本地大模型)
*   **存储空间**: 至少 10GB 可用空间 (用于存储模型和向量索引)
*   **Python**: 版本 **3.11** 或更高

---

## 🛠️ 2. 软件准备

在开始之前，请安装以下工具：

### 2.1 安装 Python 3.11+
从 [python.org](https://www.python.org/downloads/) 下载并安装。
*   *Windows 用户*: 安装时请务必勾选 **"Add Python to PATH"**。

### 2.2 安装 Ollama (核心依赖)
本系统依赖 **Ollama** 服务来运行本地的大语言模型 (LLM)。

1.  **下载与安装**：
    访问 [ollama.com](https://ollama.com) 下载对应系统的安装包并完成安装。

2.  **验证服务运行**：
    安装完成后，Ollama 通常会自动在后台运行（默认端口 `11434`）。打开终端输入以下命令验证：
    ```bash
    ollama --version
    # 正常应返回版本号，例如: ollama version is 0.1.20
    ```

3.  **下载模型 (关键步骤)**：
    系统通过 Python 代码直接调用 Ollama 接口。你需要预先下载好 UI 界面中预设的模型。请在终端执行：
    ```bash
    # 下载 Qwen2.5 (推荐中文使用)
    ollama pull qwen2.5:7b
    
    # 或者下载 Llama3
    ollama pull llama3:8b
    ```
    > ⚠️ **注意**：请确保下载的模型名称与 `src/kb/ui/app.py` 里的 `st.selectbox` 选项一致。默认配置为 `qwen3:8b` (请根据实际情况调整代码或下载对应模型)。

#### 🔗 关于连接配置
*   **默认连接**: 本项目使用 `ollama` 官方 Python 库，默认连接到 `http://localhost:11434`。
*   **无需手动配置**: 只要 Ollama 桌面端正在运行，Streamlit 应用就能自动发现并调用它。
*   **远程部署**: 如果你的 Ollama 跑在另一台机器上，需在运行 Streamlit 前设置环境变量：
    ```bash
    set OLLAMA_HOST=http://你的IP:11434
    ```

### 2.3 安装 Git (可选，推荐)
从 [git-scm.com](https://git-scm.com/downloads) 下载。

---

## 📦 3. 安装步骤

### 3.1 获取代码
将项目文件夹解压到你期望的位置 (例如 `C:\Work\local-kb`)。

### 3.2 创建虚拟环境
强烈建议使用虚拟环境来管理 Python 依赖，避免冲突。

在项目根目录下打开终端 (PowerShell 或 CMD)：

```bash
# 1. 创建虚拟环境 (名为 .venv)
python -m venv .venv

# 2. 激活虚拟环境
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# Windows (CMD):
.\.venv\Scripts\activate.bat
# Linux/Mac:
source .venv/bin/activate
```

### 3.3 安装依赖
在虚拟环境激活状态下（命令行前会有 `(.venv)` 提示），安装所需的 Python 包：

```bash
pip install -r requirements.txt
```

---

## 🚀 4. 运行应用

### 4.1 启动系统
执行以下命令启动 Streamlit 应用：

```bash
streamlit run src/kb/ui/app.py
```

### 4.2 访问界面
浏览器通常会自动打开，如果没有，请访问：
👉 **http://localhost:8505**

---

## 📂 5. 数据管理 (可选)
*   **添加文档**: 你可以通过 UI 界面上传，也可以直接将文件放入 `data/raw/` 文件夹。
*   **重置索引**: 如果需要清空知识库，可以直接删除 `data/index/` 文件夹下的内容。

---

## ❓ 常见问题 (Troubleshooting)

**Q: "ModuleNotFoundError" 或 "ImportError"**
A: 请确保你已经激活了虚拟环境（命令行前显示 `(.venv)`），并且已经成功运行了 `pip install -r requirements.txt`。

**Q: 无法连接到 Ollama / Connection failed**
A: 请确认 Ollama 应用程序正在后台运行（检查任务栏图标），并且你已经运行过 `ollama pull` 下载了对应的模型。

**Q: "Torch not compiled with CUDA enabled"**
A: 这通常意味着你的 PyTorch 正在使用 CPU 运行。系统设计可以兼容 CPU，但速度会较慢。如果你有 NVIDIA 显卡并希望加速，请前往 [pytorch.org](https://pytorch.org/get-started/locally/) 按照指引安装配合你 CUDA 版本的 PyTorch。
