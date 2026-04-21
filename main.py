import asyncio
import json
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from engine.runner import BenchmarkRunner
from agent.main_agent import MainAgent
from engine.retrieval_eval import RetrievalEvaluator
from engine.llm_judge import LLMJudge

class ExpertEvaluator:
    def __init__(self):
        self.retrieval_eval = RetrievalEvaluator()

    async def score(self, case, resp, judge_result): 
        expected_id = case.get("doc_id", "N/A")
        retrieved_ids = resp.get("metadata", {}).get("sources", [])
        
        hit_rate = self.retrieval_eval.calculate_hit_rate(expected_id, retrieved_ids)
        mrr = self.retrieval_eval.calculate_mrr(expected_id, retrieved_ids)
        
        # Lấy điểm từ Judge (Accuracy, Tone, Safety) thay vì Faithfulness/Relevancy
        return {
            "accuracy": judge_result.get("accuracy", 0) / 5.0, 
            "tone": judge_result.get("tone", 0) / 5.0,
            "safety": judge_result.get("safety", 0) / 5.0,
            "retrieval": {"hit_rate": hit_rate, "mrr": mrr}
        }

async def run_benchmark_with_results(agent_version: str):
    print(f"🚀 Khởi động Benchmark cho {agent_version}...")

    if not os.path.exists("data/golden_set.jsonl"):
        print("❌ Thiếu data/golden_set.jsonl.")
        return None, None

    with open("data/golden_set.jsonl", "r", encoding="utf-8") as f:
        dataset = [json.loads(line) for line in f if line.strip()]

    version_key = "v2" if "V2" in agent_version else "v1"
    agent = MainAgent(version=version_key)
    
    runner = BenchmarkRunner(agent, ExpertEvaluator(), LLMJudge())
    results = await runner.run_all(dataset, batch_size=5)

    total = len(results)
    summary = {
        "metadata": {"version": agent_version, "total": total, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")},
        "metrics": {
            "avg_score": sum(r["judge"]["final_score"] for r in results) / total,
            "hit_rate": sum(r["ragas"]["retrieval"]["hit_rate"] for r in results) / total,
            "avg_accuracy": sum(r["judge"]["accuracy"] for r in results) / total,
            "avg_tone": sum(r["ragas"]["tone"] for r in results) / total,
            "avg_safety": sum(r["ragas"]["safety"] for r in results) / total,
            "agreement_rate": sum(r["judge"]["agreement_rate"] for r in results) / total,
            "avg_latency": sum(r["latency"] for r in results) / total,
            "total_tokens": sum(r["tokens"] for r in results)
        }
    }
    return results, summary

async def main():
    v1_results, v1_summary = await run_benchmark_with_results("Agent_V1_Base")
    v2_results, v2_summary = await run_benchmark_with_results("Agent_V2_Optimized")
    
    if not v1_summary or not v2_summary:
        return

    print("\n📊 --- KẾT QUẢ THỰC TẾ ---")
    print(f"V1 Score: {v1_summary['metrics']['avg_score']:.2f} | Latency: {v1_summary['metrics']['avg_latency']:.2f}s")
    print(f"V2 Score: {v2_summary['metrics']['avg_score']:.2f} | Latency: {v2_summary['metrics']['avg_latency']:.2f}s")
    
    os.makedirs("reports", exist_ok=True)
    v2_summary["regression"] = {"v1_score": v1_summary["metrics"]["avg_score"], "delta": v2_summary["metrics"]["avg_score"] - v1_summary["metrics"]["avg_score"]}
    
    with open("reports/summary.json", "w", encoding="utf-8") as f:
        json.dump(v2_summary, f, ensure_ascii=False, indent=2)
    with open("reports/benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(v2_results, f, ensure_ascii=False, indent=2)

    print(f"\n📂 Đã lưu báo cáo vào thư mục reports/")

if __name__ == "__main__":
    asyncio.run(main())
