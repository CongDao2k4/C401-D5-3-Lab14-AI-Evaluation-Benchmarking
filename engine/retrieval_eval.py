from typing import List, Dict, Union

class RetrievalEvaluator:
    def __init__(self):
        pass

    def calculate_hit_rate(self, expected_ids: Union[str, List[str]], retrieved_ids: List[str], top_k: int = 3) -> float:
        """
        Tính toán xem ít nhất 1 trong expected_ids có nằm trong top_k của retrieved_ids không.
        """
        if isinstance(expected_ids, str):
            expected_ids = [expected_ids]
            
        top_retrieved = retrieved_ids[:top_k]
        # Nếu bất kỳ ID mong đợi nào nằm trong top K kết quả trả về -> Hit
        hit = any(doc_id in top_retrieved for doc_id in expected_ids)
        return 1.0 if hit else 0.0

    def calculate_mrr(self, expected_ids: Union[str, List[str]], retrieved_ids: List[str]) -> float:
        """
        Tính Mean Reciprocal Rank (MRR).
        Tìm vị trí xuất hiện sớm nhất của một expected_id trong retrieved_ids.
        MRR = 1 / position (1-indexed). Nếu không thấy thì là 0.
        """
        if isinstance(expected_ids, str):
            expected_ids = [expected_ids]

        for i, doc_id in enumerate(retrieved_ids):
            if doc_id in expected_ids:
                return 1.0 / (i + 1)
        return 0.0

    async def evaluate_batch(self, results: List[Dict]) -> Dict:
        """
        Tính toán trung bình Hit Rate và MRR cho toàn bộ kết quả benchmark.
        """
        total_hit_rate = 0.0
        total_mrr = 0.0
        count = len(results)

        if count == 0:
            return {"avg_hit_rate": 0.0, "avg_mrr": 0.0}

        for res in results:
            # Dữ liệu lấy từ cấu trúc kết quả trong runner.py
            metrics = res.get("ragas", {}).get("retrieval", {})
            total_hit_rate += metrics.get("hit_rate", 0.0)
            total_mrr += metrics.get("mrr", 0.0)

        return {
            "avg_hit_rate": total_hit_rate / count,
            "avg_mrr": total_mrr / count
        }
