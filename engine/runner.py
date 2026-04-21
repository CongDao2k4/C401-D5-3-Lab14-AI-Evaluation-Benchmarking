import asyncio
import time
from typing import List, Dict

class BenchmarkRunner:
    def __init__(self, agent, evaluator, judge):
        self.agent = agent
        self.evaluator = evaluator
        self.judge = judge

    async def run_single_test(self, test_case: Dict) -> Dict:
        start_time = time.perf_counter()
        
        # 1. Gọi Agent (Lấy câu trả lời thực và latency thực)
        response = await self.agent.query(test_case["question"])
        # Ưu tiên lấy latency thực từ agent nếu có, nếu không thì dùng latency đo tại runner
        agent_latency = response.get("metadata", {}).get("latency", time.perf_counter() - start_time)
        
        # 2. Chạy Multi-Judge (Lấy điểm Faithfulness, Relevancy thực từ AI)
        judge_result = await self.judge.evaluate_multi_judge(
            test_case["question"], 
            response["answer"], 
            test_case["expected_answer"],
            response.get("contexts", [])
        )
        
        # 3. Chạy RAGAS/Retrieval metrics
        ragas_scores = await self.evaluator.score(test_case, response, judge_result)
        
        return {
            "test_case": test_case["question"],
            "agent_response": response["answer"],
            "latency": agent_latency,
            "tokens": response.get("metadata", {}).get("tokens", 0),
            "ragas": ragas_scores,
            "judge": judge_result,
            "status": "fail" if judge_result["accuracy"] < 3 else "pass"
        }

    async def run_all(self, dataset: List[Dict], batch_size: int = 5) -> List[Dict]:
        results = []
        for i in range(0, len(dataset), batch_size):
            batch = dataset[i:i + batch_size]
            tasks = [self.run_single_test(case) for case in batch]
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)
        return results
