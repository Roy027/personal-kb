import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

import streamlit as st
import time
import pandas as pd
from typing import List
import threading
import socket
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from src.kb.rag.answer import AnswerEngine
from src.kb.schema import Document
from src.kb.chunking.chunker import Chunker
from src.kb.ingestion.pdf_loader import load_pdf
from src.kb.ingestion.html_loader import load_html

# Page Config
st.set_page_config(
    page_title="Local KB RAG",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CSS Styling ---
st.markdown("""
<style>
    .chat-message {
        padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem; display: flex
    }
    .chat-message.user {
        background-color: #2b313e; color: #ffffff;
    }
    .chat-message.bot {
        background-color: #f0f2f6; color: #000000;
    }
</style>
""", unsafe_allow_html=True)

# --- File Server Initialization ---
@st.cache_resource
def start_file_server(start_port=8000, root_directory="./data/raw"):
    """
    Starts a background HTTP server to serve files from root_directory.
    Dynamically finds an available port starting from start_port.
    """
    port = start_port
    # Find available port
    while port < 65535:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                # Bind to all interfaces to ensure accessibility
                s.bind(("0.0.0.0", port))
            break
        except OSError:
            port += 1
    
    # Define handler
    class DataHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            # Get absolute path to avoid working directory issues
            abs_root = os.path.abspath(root_directory)
            super().__init__(*args, directory=abs_root, **kwargs)
        
        def log_message(self, format, *args):
            # Suppress server logs to keep console clean
            pass
    
    # Start server in daemon thread
    def run_server():
        # Listen on all interfaces
        server = ThreadingHTTPServer(("0.0.0.0", port), DataHandler)
        server.serve_forever()
    
    t = threading.Thread(target=run_server, daemon=True)
    t.start()
    
    print(f"📂 File Server started on port {port}")
    return port

# Initialize file server
FILE_SERVER_PORT = start_file_server()

# Determine the correct IP address for the link
# If running locally, localhost is fine, but for remote access (e.g. --server.address 0.0.0.0), 
# we need the actual LAN IP.
try:
    # Connect to a public DNS to get the most likely LAN IP (doesn't actually send data)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80))
        HOST_IP = s.getsockname()[0]
except Exception:
    # Fallback if no network
    HOST_IP = "localhost"

FILE_URL_BASE = f"http://{HOST_IP}:{FILE_SERVER_PORT}"
print(f"🔗 File Links will use: {FILE_URL_BASE}")
# --- Helpers ---

LOADERS = {
    ".pdf": load_pdf,
    ".html": load_html,
    ".htm": load_html
}

def save_uploaded_file(uploaded_file):
    save_dir = "./data/raw"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    file_path = os.path.join(save_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def ingest_file(file_path, engine):
    """
    Ingests a single file into the active vector store.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in LOADERS:
        st.error(f"Unsupported file format: {ext}")
        return

    # 1. Load (加载)
    status = st.empty()
    progress = st.progress(0)
    
    status.write(f"📄 正在加载文档：{os.path.basename(file_path)}...")
    loader = LOADERS[ext]
    documents = loader(file_path)
    progress.progress(30)
    
    if not documents:
        st.warning("未检测到文本内容。")
        return

    # 2. Chunk (切分)
    status.write(f"✂️ 正在切分 {len(documents)} 页内容...")
    chunker = Chunker()
    chunked_docs = chunker.split_documents(documents)
    progress.progress(60)

    # 3. Embed & Index (向量化)
    status.write(f"🧠 正在生成向量 (共 {len(chunked_docs)} 个切片，CPU 模式请稍候)...")
    
    # Access internal components from engine
    # structure: engine -> retriever -> embedder/vector_store
    embedder = engine.retriever.embedder
    vector_store = engine.retriever.vector_store
    
    embeddings = embedder.embed_documents(chunked_docs)
    progress.progress(90)
    
    status.write("💾 保存索引中...")
    vector_store.add_documents(chunked_docs, embeddings)
    vector_store.save()
    progress.progress(100)
    
    status.success(f"成功处理文档：{os.path.basename(file_path)}！")
    time.sleep(1)
    status.empty()
    progress.empty()

@st.cache_resource(show_spinner="正在加载 RAG 引擎...")
def get_engine(model_name: str):
    return AnswerEngine(index_path="./data/index", llm_model=model_name)

# --- Sidebar ---
with st.sidebar:
    st.title("⚙️ 系统设置")
    
    st.markdown("### 模型配置")
    llm_model = st.selectbox("LLM 模型", ["qwen3:8b", "llama3:8b"], index=0)
    
    st.markdown("### 检索参数")
    top_k = st.slider("初筛数量 (Recall Top-K)", 5, 50, 20)
    top_n = st.slider("精排数量 (Rerank Top-N)", 1, 20, 3)
    
    st.markdown("---")
    if st.button("清空对话记录", type="primary"):
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("---")
    st.caption("v0.2.1 | Local Knowledge Base")

# --- Initial Load ---
try:
    engine = get_engine(llm_model)
except Exception as e:
    st.error(f"引擎加载失败: {e}")
    st.stop()

# --- Main Interface ---
st.title("📚 本地知识库助手")

# -----------------------------------------------------------------------------
# Dynamic Sidebar File Filter using Engine
with st.sidebar:
    st.markdown("### 📚 知识库范围")
    
    selected_files = None # Default to None = All
    
    if hasattr(engine.retriever.vector_store, 'get_indexed_files'):
        files_data = engine.retriever.vector_store.get_indexed_files()
        # files_data = [{'filename': 'x.pdf', 'chunks': 10}, ...]
        
        if files_data:
            all_filenames = [f['filename'] for f in files_data]
            
            # Session State for Persistence
            if "file_states" not in st.session_state:
                st.session_state.file_states = {}
            
            # Sync: New files default to True
            for f in all_filenames:
                if f not in st.session_state.file_states:
                    st.session_state.file_states[f] = True
            
            # Build DataFrame from State
            df_data = []
            for f_data in files_data:
                fname = f_data['filename']
                is_selected = st.session_state.file_states.get(fname, True)
                df_data.append({
                    "启用": is_selected,
                    "文件名": fname,
                    "切片": f_data['chunks']
                })
            
            df_filter = pd.DataFrame(df_data)
            
            with st.expander(f"选择文件 ({len(all_filenames)})", expanded=False):
                edited_df = st.data_editor(
                    df_filter,
                    column_config={
                        "启用": st.column_config.CheckboxColumn(required=True),
                        "文件名": st.column_config.TextColumn(disabled=True),
                        "切片": st.column_config.NumberColumn(disabled=True)
                    },
                    hide_index=True,
                    width='stretch',
                    key="file_filter_editor"
                )
            
            # Update State & Get Selected
            selected_files = []
            for index, row in edited_df.iterrows():
                fname = row["文件名"]
                is_active = row["启用"]
                st.session_state.file_states[fname] = is_active
                if is_active:
                    selected_files.append(fname)
            
            st.caption(f"已选 {len(selected_files)} / {len(all_filenames)} 个文档")

# -----------------------------------------------------------------------------

tab1, tab2 = st.tabs(["💬 智能问答", "🗃️ 知识库管理"])

# === TAB 1: CHAT ===
with tab1:
    # Initialize Msg
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "sources" in msg and msg["sources"]:
                with st.expander("📚 查看引用来源"):
                    for i, doc in enumerate(msg["sources"], 1):
                        source = os.path.basename(doc.metadata.get("source", "未知来源"))
                        page = doc.metadata.get("page_number", "-")
                        score = doc.metadata.get("rerank_score", 0.0)
                        
                        # Build clickable link
                        from urllib.parse import quote
                        encoded_filename = quote(source)
                        if page != "-" and source.lower().endswith('.pdf'):
                            file_link = f"{FILE_URL_BASE}/{encoded_filename}#page={page}"
                            st.markdown(f"**{i}. [📄 {source}]({file_link})** (页码: {page}, 相关度: {score:.4f})", unsafe_allow_html=True)
                        else:
                            st.markdown(f"**{i}. {source}** (页码: {page}, 相关度: {score:.4f})")
                        
                        st.caption(doc.content[:300] + "...")

    # Chat Input
    if prompt := st.chat_input("请输入你的问题..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("正在思考与检索..."):
                answer, sources = engine.answer(prompt, top_k=top_k, top_n=top_n, file_filters=selected_files)
            
            st.markdown(answer)
            
            if sources:
                with st.expander("📚 查看引用来源"):
                    for i, doc in enumerate(sources, 1):
                        source = os.path.basename(doc.metadata.get("source", "未知来源"))
                        page = doc.metadata.get("page_number", "-")
                        score = doc.metadata.get("rerank_score", 0.0)
                        
                        # Build clickable link
                        from urllib.parse import quote
                        encoded_filename = quote(source)
                        if page != "-" and source.lower().endswith('.pdf'):
                            file_link = f"{FILE_URL_BASE}/{encoded_filename}#page={page}"
                            st.markdown(f"**{i}. [📄 {source}]({file_link})** (页码: {page}, 相关度: {score:.4f})", unsafe_allow_html=True)
                        else:
                            st.markdown(f"**{i}. {source}** (页码: {page}, 相关度: {score:.4f})")
                        
                        st.caption(doc.content)
            
            st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})

# === TAB 2: KNOWLEDGE BASE ===
with tab2:
    st.header("文档管理")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📂 已收录文档")
        # Get file stats
        if hasattr(engine.retriever.vector_store, 'get_indexed_files'):
            files_data = engine.retriever.vector_store.get_indexed_files()
            if files_data:
                df = pd.DataFrame(files_data).rename(columns={"filename": "文件名", "chunks": "切片数量"})
                st.dataframe(df, width='stretch')
                st.caption(f"当前总文档数: {len(df)}")
            else:
                st.info("暂无已索引的文档。")
        else:
            st.warning("VectorStore 未实现 'get_indexed_files' 功能。")

    with col2:
        st.subheader("⬆️ 上传新文档")
        uploaded_file = st.file_uploader("选择 PDF 或 HTML 文件", type=["pdf", "html"])
        
        if uploaded_file:
            if st.button("开始导入", type="primary"):
                try:
                    # Save
                    file_path = save_uploaded_file(uploaded_file)
                    # Ingest
                    ingest_file(file_path, engine)
                    st.rerun() # Refresh list
                except Exception as e:
                    st.error(f"导入失败: {e}")
