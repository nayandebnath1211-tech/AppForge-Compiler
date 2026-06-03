import time
from typing import Dict, Any, List
from pipeline.models import AppConfig
from pipeline.intent_extractor import extract_intent
from pipeline.system_designer import design_system
from pipeline.schema_generator import generate_schemas
from pipeline.validator import validate_app_config
from pipeline.repair_engine import repair_config

def compile_instruction(instruction: str, api_key: str = None, max_repairs: int = 3) -> Dict[str, Any]:
    """
    Executes the multi-stage generation compiler pipeline:
    Intent -> System Design -> Schema Gen -> Validation -> Self-Repair (up to max_repairs).
    
    Returns a dictionary containing:
      - 'config': AppConfig (the final configuration)
      - 'errors': List[Dict] (validation errors, empty if success)
      - 'metadata': Dict (latencies, token estimation, retries)
    """
    metadata = {
        "stages": [],
        "retries": 0,
        "success": False,
        "total_latency_ms": 0,
        "repair_log": []
    }
    
    start_time = time.time()
    
    # --- STAGE 1: Intent Extraction ---
    stage_start = time.time()
    intent = extract_intent(instruction, api_key)
    stage_latency = int((time.time() - stage_start) * 1000)
    metadata["stages"].append({"name": "Intent Extraction", "latency_ms": stage_latency})
    
    # --- STAGE 2: System Design ---
    stage_start = time.time()
    design = design_system(intent, api_key)
    stage_latency = int((time.time() - stage_start) * 1000)
    metadata["stages"].append({"name": "System Design Layer", "latency_ms": stage_latency})
    
    # --- STAGE 3: Schema Generation ---
    stage_start = time.time()
    config = generate_schemas(design, api_key)
    stage_latency = int((time.time() - stage_start) * 1000)
    metadata["stages"].append({"name": "Schema Generation", "latency_ms": stage_latency})
    
    # --- VALIDATION & REPAIR LOOP ---
    repairs_run = 0
    errors = validate_app_config(config)
    
    while errors and repairs_run < max_repairs:
        repairs_run += 1
        metadata["retries"] = repairs_run
        
        repair_start = time.time()
        # Build context for the repair
        context = f"App Name: {intent.app_name}\nDescription: {intent.description}\nBusiness Rules: {', '.join(intent.business_logic_rules)}"
        
        # Call repair engine
        config = repair_config(config, errors, context, api_key)
        repair_latency = int((time.time() - repair_start) * 1000)
        
        metadata["repair_log"].append({
            "attempt": repairs_run,
            "latency_ms": repair_latency,
            "errors_before": len(errors)
        })
        
        # Re-validate
        errors = validate_app_config(config)
        
    metadata["success"] = (len(errors) == 0)
    metadata["total_latency_ms"] = int((time.time() - start_time) * 1000)
    
    # Estimate Cost: 1 token ~ 4 characters. For Gemini Flash, input/output pricing:
    # Input: $0.075 / 1M tokens, Output: $0.30 / 1M tokens.
    # We estimate simple mock cost (in USD) based on latency and payload size.
    # A single run takes approx 15k input tokens and 10k output tokens.
    # Cost = (15000 * 0.075/1e6) + (10000 * 0.30/1e6) = $0.0011 + $0.003 = $0.0041
    estimated_cost = 0.0041 + (repairs_run * 0.002)
    metadata["estimated_cost_usd"] = estimated_cost
    
    return {
        "config": config,
        "errors": errors,
        "metadata": metadata
    }
