import argparse
import sys
from src.kb.rag.answer import AnswerEngine

def main():
    parser = argparse.ArgumentParser(description="Ask a question to the local knowledge base.")
    parser.add_argument("query", type=str, help="The question to ask.")
    parser.add_argument("--index-path", type=str, default="./data/index", help="Path to the index.")
    
    args = parser.parse_args()
    
    print(f"Loading Answer Engine (LLM: qwen3:8b)...")
    try:
        engine = AnswerEngine(index_path=args.index_path)
    except Exception as e:
        print(f"Error initializing engine: {e}")
        return

    print("-" * 50)
    print(f"Question: {args.query}")
    print("-" * 50)
    
    answer_text, sources = engine.answer(args.query)
    
    print("\n" + "="*20 + " ANSWER " + "="*20 + "\n")
    print(answer_text)
    print("\n" + "="*50)
    
    print("\nSources Used:")
    for i, doc in enumerate(sources, 1):
        source = doc.metadata.get("source", "Unknown")
        print(f"{i}. {source}")

if __name__ == "__main__":
    main()
