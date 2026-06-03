import os
import json
import time
from typing import Dict, Any, List
from evaluation.dataset import PRODUCT_PROMPTS, EDGE_PROMPTS
from pipeline.compiler import compile_instruction

class AppForgeEvaluator:
    """
    Runs automated evaluation metrics for the multi-stage compiler pipeline 
    against standard product requests and edge cases.
    """
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.results_dir = os.path.join(os.path.dirname(__file__), "results")
        os.makedirs(self.results_dir, exist_ok=True)

    def run_evaluation(self) -> Dict[str, Any]:
        """
        Runs compilation on all 20 prompts, records detailed metrics, 
        and returns a summary report.
        """
        print("Starting AppForge Compiler Evaluation Suite...")
        
        product_results = []
        edge_results = []
        
        # 1. Evaluate Product Prompts
        for item in PRODUCT_PROMPTS:
            print(f"Compiling Product Prompt: {item['name']}...")
            res = self._evaluate_prompt(item, "product")
            product_results.append(res)
            
        # 2. Evaluate Edge Case Prompts
        for item in EDGE_PROMPTS:
            print(f"Compiling Edge Case: {item['name']}...")
            res = self._evaluate_prompt(item, "edge_case")
            edge_results.append(res)
            
        all_results = product_results + edge_results
        
        # 3. Calculate Summary Metrics
        total_runs = len(all_results)
        successful_runs = sum(1 for r in all_results if r["success"])
        success_rate = (successful_runs / total_runs) * 100 if total_runs > 0 else 0.0
        
        prod_runs = len(product_results)
        prod_success = sum(1 for r in product_results if r["success"])
        prod_success_rate = (prod_success / prod_runs) * 100 if prod_runs > 0 else 0.0
        
        edge_runs = len(edge_results)
        edge_success = sum(1 for r in edge_results if r["success"])
        edge_success_rate = (edge_success / edge_runs) * 100 if edge_runs > 0 else 0.0
        
        avg_latency = sum(r["latency_ms"] for r in all_results) / total_runs if total_runs > 0 else 0.0
        avg_retries = sum(r["retries"] for r in all_results) / total_runs if total_runs > 0 else 0.0
        total_cost = sum(r["cost_usd"] for r in all_results)
        
        # Breakdown failures by type
        failure_types = {}
        for r in all_results:
            if not r["success"]:
                for err in r["errors"]:
                    cat = err.get("category", "UNKNOWN")
                    failure_types[cat] = failure_types.get(cat, 0) + 1

        summary = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_prompts": total_runs,
            "success_rate": round(success_rate, 2),
            "product_success_rate": round(prod_success_rate, 2),
            "edge_case_success_rate": round(edge_success_rate, 2),
            "average_latency_ms": int(avg_latency),
            "average_retries": round(avg_retries, 2),
            "total_estimated_cost_usd": round(total_cost, 4),
            "failure_categories": failure_types,
            "results": {
                "products": product_results,
                "edge_cases": edge_results
            }
        }
        
        # Write results to file
        output_path = os.path.join(self.results_dir, "eval_latest.json")
        with open(output_path, "w") as f:
            json.dump(summary, f, indent=2)
            
        print("Evaluation Suite complete. Results saved.")
        return summary

    def _evaluate_prompt(self, item: Dict[str, str], category: str) -> Dict[str, Any]:
        """Runs compile on a single prompt and returns metric logs."""
        try:
            res = compile_instruction(item["prompt"], self.api_key)
            config = res["config"]
            errors = res["errors"]
            metadata = res["metadata"]
            
            return {
                "id": item["id"],
                "name": item["name"],
                "prompt": item["prompt"],
                "category": category,
                "success": metadata["success"],
                "latency_ms": metadata["total_latency_ms"],
                "retries": metadata["retries"],
                "cost_usd": metadata["estimated_cost_usd"],
                "errors": errors,
                "stages": metadata["stages"]
            }
        except Exception as e:
            return {
                "id": item["id"],
                "name": item["name"],
                "prompt": item["prompt"],
                "category": category,
                "success": False,
                "latency_ms": 0,
                "retries": 0,
                "cost_usd": 0.0,
                "errors": [{"category": "SYSTEM", "message": str(e)}],
                "stages": []
            }

if __name__ == "__main__":
    evaluator = AppForgeEvaluator()
    report = evaluator.run_evaluation()
    print(json.dumps(report, indent=2))
