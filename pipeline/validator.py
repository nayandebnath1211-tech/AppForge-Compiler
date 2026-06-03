from typing import List, Dict, Any
from pipeline.models import AppConfig

def validate_app_config(config: AppConfig) -> List[Dict[str, Any]]:
    """
    Validates semantic consistency across all layers of the generated AppConfig.
    Returns a list of structured errors/warnings. If empty, the config is fully consistent.
    """
    errors = []

    # Helper maps
    db_tables = {table.name: table for table in config.db_schema.tables}
    api_endpoints = {(ep.path, ep.method.upper()): ep for ep in config.api_schema.endpoints}
    api_paths = {ep.path for ep in config.api_schema.endpoints}
    auth_roles = set(config.auth_schema.roles)

    # 1. Database Schema Integrity Checks
    for table_name, table in db_tables.items():
        # Check foreign keys
        for fk in table.foreign_keys:
            if fk.reference_table not in db_tables:
                errors.append({
                    "category": "DATABASE",
                    "severity": "ERROR",
                    "message": f"Table '{table_name}' has a foreign key referencing a non-existent table '{fk.reference_table}'.",
                    "context": {"table": table_name, "fk": fk.model_dump()}
                })
            else:
                ref_table = db_tables[fk.reference_table]
                ref_cols = {col.name for col in ref_table.columns}
                if fk.reference_column not in ref_cols:
                    errors.append({
                        "category": "DATABASE",
                        "severity": "ERROR",
                        "message": f"Foreign key in table '{table_name}' references non-existent column '{fk.reference_column}' in table '{fk.reference_table}'.",
                        "context": {"table": table_name, "fk": fk.model_dump()}
                    })
                
        # Check indexes
        col_names = {col.name for col in table.columns}
        for idx in table.indexes:
            if idx not in col_names:
                errors.append({
                    "category": "DATABASE",
                    "severity": "WARNING",
                    "message": f"Table '{table_name}' defines an index on non-existent column '{idx}'.",
                    "context": {"table": table_name, "index_column": idx}
                })

    # 2. API Schema and DB Alignment Checks
    for ep in config.api_schema.endpoints:
        # Check role permission configuration
        for role in ep.allowed_roles:
            if role not in auth_roles:
                errors.append({
                    "category": "AUTH",
                    "severity": "ERROR",
                    "message": f"API Endpoint '{ep.method} {ep.path}' allows role '{role}', which is not defined in the Auth roles.",
                    "context": {"path": ep.path, "method": ep.method, "role": role}
                })

        # Check DB Operations reference existing tables
        for op in ep.db_operations:
            if op.table not in db_tables:
                errors.append({
                    "category": "CROSS_LAYER",
                    "severity": "ERROR",
                    "message": f"API Endpoint '{ep.method} {ep.path}' executes DB operation '{op.action}' on non-existent table '{op.table}'.",
                    "context": {"path": ep.path, "method": ep.method, "operation": op.model_dump()}
                })

    # 3. UI Schema Alignment Checks
    for page in config.ui_schema.pages:
        # Check page level roles
        for role in page.allowed_roles:
            if role not in auth_roles:
                errors.append({
                    "category": "AUTH",
                    "severity": "ERROR",
                    "message": f"UI Page '{page.name}' ({page.route}) restricts access to role '{role}', which is not defined in the Auth roles.",
                    "context": {"page": page.name, "route": page.route, "role": role}
                })

        for comp in page.components:
            # Check API binding alignment
            if comp.api_binding:
                binding = comp.api_binding
                key = (binding.path, binding.method.upper())
                if key not in api_endpoints:
                    errors.append({
                        "category": "CROSS_LAYER",
                        "severity": "ERROR",
                        "message": f"UI Component '{comp.id}' on Page '{page.name}' binds to non-existent API endpoint '{binding.method} {binding.path}'.",
                        "context": {"page": page.name, "component": comp.id, "binding": binding.model_dump()}
                    })

            # Check UI Action endpoints
            for action in comp.actions:
                if action.action_type == "api_call":
                    method = "GET"
                    if action.payload and "method" in action.payload:
                        method = action.payload["method"].upper()
                    
                    key = (action.target, method)
                    if key not in api_endpoints:
                        errors.append({
                            "category": "CROSS_LAYER",
                            "severity": "ERROR",
                            "message": f"UI Action in component '{comp.id}' triggers non-existent API endpoint '{method} {action.target}'.",
                            "context": {"page": page.name, "component": comp.id, "action": action.model_dump()}
                        })
                elif action.action_type == "navigate":
                    # Check if target page route exists
                    routes = {p.route for p in config.ui_schema.pages}
                    if action.target not in routes and not action.target.startswith("http"):
                        errors.append({
                            "category": "UI",
                            "severity": "WARNING",
                            "message": f"UI Button in component '{comp.id}' navigates to route '{action.target}', which does not match any page route.",
                            "context": {"page": page.name, "component": comp.id, "target_route": action.target}
                        })

    # 4. Logic Rules and Gating Alignment
    for rule in config.logic_schema.rules:
        # Check rule trigger event
        # Format e.g.: "api:before_call:/api/contacts:POST" or "api:before_call:/api/contacts"
        trigger = rule.trigger_event
        if trigger.startswith("api:"):
            parts = trigger.split(":")
            if len(parts) >= 3:
                api_path = parts[2]
                method = parts[3].upper() if len(parts) > 3 else "GET"
                key = (api_path, method)
                # Check if it exists as is or matches path prefix
                if key not in api_endpoints and api_path not in api_paths:
                    errors.append({
                        "category": "LOGIC",
                        "severity": "WARNING",
                        "message": f"Logic Rule '{rule.id}' triggers on API path '{api_path}' which was not found in API schemas.",
                        "context": {"rule_id": rule.id, "trigger_event": trigger}
                    })

    return errors
