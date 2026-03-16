from llama_cpp import Llama
from typing import Optional, AsyncGenerator
import os


class LlamaEngine:
    """LLaMA.cpp引擎封装"""
    
    def __init__(
        self,
        model_path: str,
        n_ctx: int = 2048,
        n_gpu_layers: int = 0,
        n_threads: int = 4
    ):
        self.model_path = model_path
        self.n_ctx = n_ctx
        
        # 检查模型文件是否存在
        if not os.path.exists(model_path):
            print(f"⚠️  模型文件不存在: {model_path}")
            print("请下载模型文件或配置正确的路径")
            self.llm = None
            return
        
        # 加载模型
        print(f"🔧 Loading LLM model: {model_path}")
        self.llm = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_gpu_layers=n_gpu_layers,
            n_threads=n_threads,
            verbose=False
        )
        print("✅ LLM model loaded")
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 256,
        temperature: float = 0.7,
        top_p: float = 0.9,
        stop: Optional[list] = None
    ) -> str:
        """生成文本"""
        if not self.llm:
            return "⚠️ LLM模型未加载,请检查模型路径"
        
        output = self.llm(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stop=stop or ["</s>", "\n\n\n"]
        )
        
        return output["choices"][0]["text"]
    
    def stream_generate(
        self,
        prompt: str,
        max_tokens: int = 256,
        temperature: float = 0.7,
        top_p: float = 0.9,
        stop: Optional[list] = None
    ):
        """流式生成文本"""
        if not self.llm:
            yield "⚠️ LLM模型未加载,请检查模型路径"
            return
        
        for chunk in self.llm(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stop=stop or ["</s>", "\n\n\n"],
            stream=True
        ):
            yield chunk["choices"][0]["text"]
    
    def build_prompt(
        self,
        system_prompt: str,
        context: str,
        user_input: str
    ) -> str:
        """构建完整提示词"""
        prompt = f"""<|system|>
{system_prompt}

{context}
</s>
<|user|>
{user_input}</s>
<|assistant|>
"""
        return prompt
