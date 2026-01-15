import streamlit as st
import time
from typing import List
from src.kb.rag.answer import AnswerEngine
from src.kb.schema import Document

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
    .reportview-container {
        background: #f0f2f6;
    }
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

# --- Sidebar ---
with st.sidebar:
    st.title("⚙️ RAG Settings")
    
    st.markdown("### Model Configuration")
    llm_model = st.selectbox("LLM Model", ["qwen3:8b", "llama3:8b", "mistral"], index=0)
    
    st.markdown("### Retrieval Parameters")
    top_k = st.slider("Recall Top-K (Vector Search)", 5, 50, 20)
    top_n = st.slider("Rerank Top-N (Final Context)", 1, 10, 3)
    
    st.markdown("---")
    if st.button("Clear Chat History", type="primary"):
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("---")
    st.markdown("v0.1.0 | Local Knowledge Base")

# --- Logic ---

@st.cache_resource(show_spinner="Loading optimized RAG engine...")
def get_engine(model_name: str):
    return AnswerEngine(index_path="./data/index", llm_model=model_name)

try:
    engine = get_engine(llm_model)
    st.success("Engine Loaded Successfully!", icon="✅")
except Exception as e:
    st.error(f"Failed to load engine: {e}")
    st.stop()

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Main Interface ---

st.title("📚 Local Knowledge Base Assistant")
st.markdown("Ask questions about your local documents. Fully private, 100% offline.")

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "sources" in msg and msg["sources"]:
            with st.expander("📚 View Sources & Evidence"):
                for i, doc in enumerate(msg["sources"], 1):
                    source = doc.metadata.get("source", "Unknown")
                    page = doc.metadata.get("page_number", "N/A")
                    score = doc.metadata.get("rerank_score", 0.0)
                    
                    st.markdown(f"**{i}. {source}** (Page: {page}, Score: {score:.4f})")
                    st.text(doc.content)

# Input
if prompt := st.chat_input("What do you want to know?"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        with st.spinner("Thinking & Retrieving..."):
            answer, sources = engine.answer(prompt, top_k=top_k, top_n=top_n)
            
        # Simulate typing effect (optional, or just stream if supported later)
        message_placeholder.markdown(answer)
        
        # Show sources
        if sources:
            with st.expander("📚 View Sources & Evidence"):
                for i, doc in enumerate(sources, 1):
                    source = doc.metadata.get("source", "Unknown")
                    page = doc.metadata.get("page_number", "N/A")
                    score = doc.metadata.get("rerank_score", 0.0)
                    
                    st.markdown(f"**{i}. {source}** (Page: {page}, Score: {score:.4f})")
                    st.caption(f"Score: {score:.4f}")
                    st.text(doc.content)
        
        st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})
