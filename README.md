# 📘 Local Local Knowledge Base（RAG）

**PRD v0.1（冻结版）**

> 项目目标：构建一个**完全本地运行**的个人/小团队知识库系统，支持 PDF / 网页 / 代码文档的检索，**以“原文证据为中心”生成结论并强制引用**，用于技术工作与知识沉淀。

---

## 1️⃣ 项目背景与目标

### 背景

* 个人长期积累大量 **PDF 技术文档、网页资料、代码说明**
* 传统笔记 / 文件夹 **检索效率低、无法跨文档推理**
* 不接受：

  * 云端 LLM API（隐私 + 成本）
  * “编造式回答”
  * 复杂 agent / 自动执行

### 核心目标

* ✅ 找到 **原文证据**
* ✅ 基于证据给出 **总结性结论**
* ✅ **强制可回溯引用**
* ✅ 完全 **本地运行**
* ✅ 支持 **中英混合**

### 明确不做（v0.x）

* ❌ 自动执行任务 / agent
* ❌ 云端模型依赖
* ❌ 实时爬虫 / 自动更新
* ❌ 高质量图片 OCR / PPT 深度理解（后续）

---

## 2️⃣ 用户与使用场景

### 用户

* 主用户：**本人**
* 次用户：**少量同事（可信环境）**

### 典型使用场景

1. “我之前看过的某个 PDF 里，对 XX 的结论是什么？”
2. “有没有文档明确提到过 YY 的限制条件？”
3. “把这几篇资料的共识总结一下，并给出处。”

---

## 3️⃣ 功能需求（Functional Requirements）

### 3.1 文档导入（Ingestion）

* 支持格式：

  * ✅ PDF（文本型）
  * ✅ HTML / 网页正文
  * ✅ 代码（.py / .md / .txt）
  * ⏸️ PPT / 图片（仅作为原文存档，不保证检索效果）
* 导入方式：

  * 手动导入
  * 按文件夹分类（作为 metadata）
* 增量导入：

  * 基于 hash / mtime
  * 未变化文档不重建索引

---

### 3.2 文档处理（Processing）

* 文本抽取 → 统一 Document Schema
* Chunk 策略：

  * 按段落 / 标题优先
  * chunk size ≈ 600–800 tokens
  * 保留文档结构信息（页码 / 段落）

---

### 3.3 向量索引（Index）

* 本地向量库（FAISS / Chroma）
* 每个 chunk 存储：

  * embedding
  * 文档来源
  * 文件路径
  * 页码 / 段落号
  * 标签 / 分类（来自文件夹）

---

### 3.4 检索（Retrieve）

* 向量检索（top-k）
* 可选 rerank（bge-reranker）
* 支持 metadata filter（按分类 / 标签）

---

### 3.5 回答生成（RAG）

* 本地 LLM
* **严格约束规则**：

  * 只能基于检索内容回答
  * 必须列出引用 chunk
  * 无证据 → 明确拒答

---

### 3.6 UI（Web）

* Streamlit
* 功能：

  * 输入问题
  * 展示答案
  * 展示引用列表（可点击原文）

---

## 4️⃣ 非功能需求（Non-Functional）

### 性能

* 支持 **1k–3k 文档**
* 单次查询 < 5s（本地）

### 可维护性

* 清晰模块拆分
* 日志可追踪
* 可扩展新文档类型

### 可靠性

* 不允许 hallucination
* 回答必须可回溯

---

## 5️⃣ 技术选型（冻结）

### 语言 / 工程

* Python 3.11+
* uv / poetry
* Git + GitHub Issues

### 模型（本地）

* Embedding：`bge-m3`
* Reranker：`bge-reranker-large`
* LLM：Qwen3 / LLaMA 3.x（8B–14B）

### 向量库

* FAISS（优先）或 Chroma（如需 metadata filter）

### UI

* Streamlit

---

## 6️⃣ 项目目录结构（最终版）

```
local-kb/
├── README.md
├── pyproject.toml
├── .env.example

├── data/
│   ├── raw/                # 原始文档（只读）
│   ├── processed/          # 解析后文本 / chunk
│   ├── index/              # 向量索引
│   └── cache/              # 临时缓存

├── src/
│   └── kb/
│       ├── ingestion/
│       │   ├── pdf_loader.py
│       │   ├── html_loader.py
│       │   └── code_loader.py
│       ├── chunking/
│       │   └── chunker.py
│       ├── embedding/
│       │   └── embedder.py
│       ├── index/
│       │   └── vector_store.py
│       ├── retrieve/
│       │   └── retriever.py
│       ├── rag/
│       │   ├── prompt.py
│       │   └── answer.py
│       ├── eval/
│       │   └── eval_set.json
│       └── ui/
│           └── app.py

├── scripts/
│   ├── ingest.py
│   ├── query.py
│   └── rebuild_index.py

└── tests/
    ├── test_chunking.py
    └── test_retrieve.py
```

---

## 7️⃣ GitHub Issues 计划（可直接创建）

### 🟢 Milestone 1：MVP 检索系统

**目标：找得到原文**

* Issue #1：项目初始化（repo / 依赖 / 结构）
* Issue #2：PDF 文本抽取模块
* Issue #3：HTML 正文抽取模块
* Issue #4：Chunk 策略实现
* Issue #5：Embedding + 向量索引
* Issue #6：CLI 查询返回原文片段

✅ 验收：CLI 输入 query → 返回 chunk + 来源

---

### 🟡 Milestone 2：RAG + 强制引用

**目标：能总结，但不胡说**

* Issue #7：检索 + rerank pipeline
* Issue #8：RAG prompt（强制引用）
* Issue #9：LLM 本地推理接口
* Issue #10：拒答机制（无证据）

✅ 验收：每条答案都有明确引用

---

### 🔵 Milestone 3：可用性与 UI

**目标：你愿意每天用**

* Issue #11：Streamlit UI
* Issue #12：metadata filter（文件夹 / 标签）
* Issue #13：增量导入机制
* Issue #14：日志与调试信息

### 🟣 Future Features (Backlog)

* **Issue #15: Support OCR for Scanned PDFs** (Pending)
    - Integrate `paddleocr` or `tesseract` to handle image-based PDFs.
    - Add logic to detect "empty text" pages and fallback to OCR.

---

## 8️⃣ 成功标准（Definition of Done）

* 我可以 **忘记文件放哪了，但还能找回结论**
* 我能 **点开引用直接看到原文**
* 我信任它 **不会编造**
* 我愿意 **持续往里丢新文档**

---

## 9️⃣ 下一步你该做什么（明确）

**现在就做：**

1. 新建 GitHub repo
2. 把这份 PRD 放进 `README.md`
3. 按 Milestone 建 Issues
4. 开始 Issue #1
