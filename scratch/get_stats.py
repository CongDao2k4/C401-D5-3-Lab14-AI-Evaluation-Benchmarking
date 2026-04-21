import json
import os

def run():
    with open('reports/summary.json', encoding='utf-8') as f:
        summary = json.load(f)
    
    with open('reports/benchmark_results.json', encoding='utf-8') as f:
        results = json.load(f)
        
    passes = len([r for r in results if r.get('status') == 'pass'])
    fails = len([r for r in results if r.get('status') == 'fail'])
    
    print("=== SUMMARY ===")
    print(f"Total: {summary['metadata']['total']}")
    print(f"Pass: {passes}, Fail: {fails}")
    print(f"Avg Score: {summary['metrics']['avg_score']:.2f}")
    print(f"Hit Rate: {summary['metrics']['hit_rate']:.2f}")
    
    # In my memory, RAGAS scores were: accuracy, tone, safety. Let's find their averages if faithfulness/relevancy aren't there.
    # We will compute from results directly to be sure.
    if len(results) > 0 and 'ragas' in results[0]:
        r_keys = results[0]['ragas'].keys()
        for k in r_keys:
            if isinstance(results[0]['ragas'][k], (int, float)):
                avg_k = sum(r['ragas'].get(k, 0) for r in results) / len(results)
                print(f"RAGAS {k}: {avg_k:.2f}")
                
    # Sort fails by score ascending to find worst 3
    failed_cases = [r for r in results if r.get('status') == 'fail']
    failed_cases.sort(key=lambda x: x['judge']['final_score'])
    
    print("\n=== TOP 3 FAILS ===")
    for i, f in enumerate(failed_cases[:3]):
        print(f"Case #{i+1}: {f['test_case']}")
        print(f"Score: {f['judge']['final_score']}")
        print(f"Hit Rate: {f['ragas'].get('retrieval', {}).get('hit_rate', 'N/A')}")
        print(f"Agent Response: {f['agent_response']}")
        print(f"Qwen Reasoning: {f['judge']['details']['qwen']['reasoning']}")
        print("---")

if __name__ == '__main__':
    run()
