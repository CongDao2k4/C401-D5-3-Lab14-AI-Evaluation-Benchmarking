import asyncio
import os
import time
from typing import List, Dict
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MainAgent:
    """
    Agent mẫu tích hợp RAG. 
    Trong thực tế, bạn nên thay thế logic này bằng hệ thống VectorDB và LLM của nhóm.
    """
    def __init__(self, version: str = "v1"):
        self.version = version
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"

    async def query(self, question: str) -> Dict:
        start_time = time.perf_counter()
        
        # 1. Retrieval
        await asyncio.sleep(0.1) 
        if self.version == "v2":
            retrieved_ids = ["doc_oracle_23ai_001", "manual_002"]
            context = "Hệ thống Oracle Database 23ai hỗ trợ AI Vector Search và cài đặt qua Docker/Linux."
        else:
            retrieved_ids = ["unknown_doc_099"]
            context = "Thông tin về Oracle Database."

        # 2. Generation
        try:
            if os.getenv("OPENAI_API_KEY"):
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": f"Sử dụng context sau để trả lời: {context}"},
                        {"role": "user", "content": question}
                    ],
                    max_tokens=200
                )
                answer = response.choices[0].message.content
                # Tính token thực tế (ước lượng 1 token ~ 4 ký tự)
                prompt_tokens = len(question + context) // 4
                completion_tokens = response.usage.completion_tokens if hasattr(response, 'usage') else len(answer) // 4
                total_tokens = prompt_tokens + completion_tokens
            else:
                answer = f"[Simulated Answer for {self.version}]"
                total_tokens = len(answer) // 4
        except Exception as e:
            answer = f"Lỗi: {str(e)}"
            total_tokens = 0

        latency = time.perf_counter() - start_time

        return {
            "answer": answer,
            "contexts": [context],
            "metadata": {
                "version": self.version,
                "sources": retrieved_ids,
                "latency": latency, # Latency thực
                "tokens": total_tokens # Token thực
            }
        }
