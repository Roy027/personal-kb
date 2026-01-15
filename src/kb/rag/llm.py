import ollama
from typing import List, Dict, Optional

class LocalLLM:
    def __init__(self, model: str = "qwen3:8b"):
        self.model = model

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = ollama.chat(model=self.model, messages=messages)
            return response['message']['content']
        except Exception as e:
            return f"Error generating response: {str(e)}"

if __name__ == "__main__":
    llm = LocalLLM()
    print("Testing LocalLLM with qwen3:8b...")
    print(llm.generate("Hello, introduced yourself in one sentence."))
