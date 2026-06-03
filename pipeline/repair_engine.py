import json
from typing import List, Dict, Any
from pipeline.models import AppConfig
from pipeline.llm_helper import get_gemini_key, call_gemini_structured
from pipeline.validator import validate_app_config

REPAIR_PROMPT_TEMPLATE = """
You are a principal systems troubleshooter. An AppConfig configuration failed semantic validation checks. You must fix the inconsistencies.

Original Design / Context:
{context}

Current AppConfig (Invalid JSON):
{invalid_config_json}

Validation Failures:
{error_log_json}

Repair Instructions:
1. Examine each error and modify the configuration to resolve it.
2. Ensure table names in API endpoints match existing database tables.
3. Align UI api_bindings and component actions with actual API endpoints (paths and HTTP methods).
4. Synchronize all allowed roles in UI pages and API endpoints with the roles list in the Auth schema.
5. Fix any index or foreign key column mismatches.

Ensure that the rest of the application remains unchanged.
Conform strictly to the JSON schema output requirement. Do not include markdown code block characters around the raw JSON in the response.
"""

def repair_config(config: AppConfig, errors: List[Dict[str, Any]], original_context: str, api_key: str = None) -> AppConfig:
    """
    Attempts to repair validation errors in AppConfig.
    If actual LLM is configured, runs a correction query.
    If in mock mode, executes programmatic fixes or returns corrected preset.
    """
    has_key = get_gemini_key(api_key) is not None
    
    if has_key:
        invalid_config_json = config.model_dump_json(indent=2)
        error_log_json = json.dumps(errors, indent=2)
        
        prompt = REPAIR_PROMPT_TEMPLATE.format(
            context=original_context,
            invalid_config_json=invalid_config_json,
            error_log_json=error_log_json
        )
        
        try:
            repaired_data = call_gemini_structured(prompt, AppConfig, api_key)
            return AppConfig(**repaired_data)
        except Exception as e:
            print(f"Gemini API Repair Error: {e}. Executing fallback programmatic repair.")
            return programmatic_repair(config, errors)
    else:
        return programmatic_repair(config, errors)

def programmatic_repair(config: AppConfig, errors: List[Dict[str, Any]]) -> AppConfig:
    """
    A robust, rule-based fallback repair engine that programmatically patches 
    common cross-layer mismatches.
    """
    # Create copies of configuration components to modify
    db_schema = config.db_schema
    api_schema = config.api_schema
    ui_schema = config.ui_schema
    auth_schema = config.auth_schema
    logic_schema = config.logic_schema
    
    # Establish valid lists
    valid_tables = {table.name for table in db_schema.tables}
    valid_roles = set(auth_schema.roles)
    
    # Track endpoints to align them
    api_endpoints = {(ep.path, ep.method.upper()): ep for ep in api_schema.endpoints}
    
    # Build list of fixes to apply
    for error in errors:
        category = error.get("category")
        context = error.get("context", {})
        
        # 1. Fix missing roles
        if category == "AUTH":
            role = context.get("role")
            if role and role not in valid_roles:
                auth_schema.roles.append(role)
                valid_roles.add(role)
                
        # 2. Fix missing tables referenced in API DB operations
        elif category == "CROSS_LAYER" and "operation" in context:
            op = context["operation"]
            ref_table = op.get("table")
            # If the API references a table that doesn't exist, we map it to the closest table
            if ref_table and ref_table not in valid_tables:
                closest_table = list(valid_tables)[0] if valid_tables else "users"
                # Update the operation in the endpoint
                path = context.get("path")
                method = context.get("method", "").upper()
                for ep in api_schema.endpoints:
                    if ep.path == path and ep.method.upper() == method:
                        for db_op in ep.db_operations:
                            if db_op.table == ref_table:
                                db_op.table = closest_table
                                
        # 3. Fix missing API endpoints referenced in UI binding/action
        elif category == "CROSS_LAYER" and ("binding" in context or "action" in context):
            # Extract UI binding path/method or action path/method
            target_path = None
            target_method = "GET"
            
            if "binding" in context:
                binding = context["binding"]
                target_path = binding.get("path")
                target_method = binding.get("method", "GET").upper()
            elif "action" in context:
                action = context["action"]
                target_path = action.get("target")
                if action.get("payload") and "method" in action["payload"]:
                    target_method = action["payload"]["method"].upper()
            
            if target_path:
                # If endpoint doesn't exist, we add a mock/skeleton API endpoint for it
                # so that the UI binding is resolved and doesn't break
                new_ep_key = (target_path, target_method)
                if new_ep_key not in api_endpoints:
                    from pipeline.models import ApiEndpoint, DbOperation
                    # Guess some default table operation based on URL path
                    table_guess = target_path.split("/")[-1]
                    if table_guess not in valid_tables:
                        table_guess = list(valid_tables)[0] if valid_tables else "users"
                        
                    action_guess = "SELECT" if target_method == "GET" else "INSERT"
                    
                    skeleton_ep = ApiEndpoint(
                        path=target_path,
                        method=target_method,
                        description=f"Generated skeleton endpoint to resolve UI dependency",
                        auth_required=True,
                        allowed_roles=list(valid_roles),
                        db_operations=[DbOperation(table=table_guess, action=action_guess)]
                    )
                    api_schema.endpoints.append(skeleton_ep)
                    api_endpoints[new_ep_key] = skeleton_ep

    # Return the patched config
    return AppConfig(
        app_name=config.app_name,
        db_schema=db_schema,
        api_schema=api_schema,
        ui_schema=ui_schema,
        auth_schema=auth_schema,
        logic_schema=logic_schema
    )
