import re
from typing import Dict, Any, List, Optional
from pipeline.models import ApiSchema, LogicSchema
from runtime.mock_db import MockDatabase

class MockApiRouter:
    """
    Simulates a backend API gateway. Resolves HTTP endpoints, enforces auth/role policies,
    runs logic/gating rules, and translates actions into SQLite database statements.
    """
    def __init__(self, api_schema: ApiSchema, logic_schema: LogicSchema, db: MockDatabase):
        self.api_schema = api_schema
        self.logic_schema = logic_schema
        self.db = db

    def handle_request(self, path: str, method: str, body: Dict[str, Any] = None, user_session: Dict[str, Any] = None) -> Dict[str, Any]:
        """Processes an incoming simulated HTTP request."""
        method = method.upper()
        body = body or {}
        user_session = user_session or {"id": None, "email": "guest@appforge.com", "role": "Anonymous", "subscription": "free"}
        
        # 1. Route Matching
        endpoint = None
        for ep in self.api_schema.endpoints:
            if ep.path == path and ep.method.upper() == method:
                endpoint = ep
                break
                
        if not endpoint:
            # Check for general pattern match (fallback)
            for ep in self.api_schema.endpoints:
                # Match /api/contacts/{id} matches
                cleaned_ep = re.sub(r'\{[a-zA-Z0-9_]+\}', r'[^/]+', ep.path)
                if re.match(f"^{cleaned_ep}$", path) and ep.method.upper() == method:
                    endpoint = ep
                    break
                    
        if not endpoint:
            return {"status": 404, "body": {"error": f"Endpoint {method} {path} not found"}}

        # 2. Auth & Role Gate Checks
        if endpoint.auth_required:
            if not user_session.get("id"):
                return {"status": 401, "body": {"error": "Unauthorized: Authentication required."}}
            
            role = user_session.get("role", "Anonymous")
            if endpoint.allowed_roles and role not in endpoint.allowed_roles:
                return {"status": 403, "body": {"error": f"Forbidden: Role '{role}' does not have access."}}

        # 3. Gating Logic Rule Evaluation (Interceptors)
        # Evaluate rules in logic_schema triggering on api calls
        for rule in self.logic_schema.rules:
            # trigger formats: "api:before_call:/api/contacts:POST" or "api:before_call:/api/contacts"
            trigger = rule.trigger_event
            is_match = False
            if trigger.startswith("api:before_call:"):
                trigger_path = trigger.split(":")[2]
                trigger_method = trigger.split(":")[3].upper() if len(trigger.split(":")) > 3 else None
                
                if trigger_path == path and (not trigger_method or trigger_method == method):
                    is_match = True
                    
            if is_match:
                # Evaluate conditions safely
                rule_triggered = False
                for cond in rule.conditions:
                    if self._eval_condition(cond, user_session, body):
                        rule_triggered = True
                        break
                        
                if rule_triggered and rule.action == "DENY":
                    return {"status": 400, "body": {"error": rule.error_message or "Request blocked by business logic rules."}}

        # 4. DB Operations Execution
        response_data = []
        try:
            for op in endpoint.db_operations:
                table_name = op.table
                action = op.action.upper()
                
                # Check that table exists in SQLite
                cursor = self.db.conn.cursor()
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
                if not cursor.fetchone():
                    return {"status": 500, "body": {"error": f"Database table '{table_name}' does not exist"}}

                if action == "SELECT":
                    sql = f"SELECT * FROM {table_name}"
                    params = []
                    # Check owner constraint
                    if op.conditions and "owner_id = user.id" in op.conditions:
                        sql += " WHERE owner_id = ?"
                        params.append(user_session.get("id"))
                    elif op.conditions and "id = request.body.id" in op.conditions:
                        sql += " WHERE id = ?"
                        params.append(body.get("id"))
                        
                    res = self.db.query(sql, tuple(params))
                    response_data.extend(res)
                    
                elif action == "INSERT":
                    # Filter body elements that match table columns
                    cursor.execute(f"PRAGMA table_info({table_name});")
                    cols = [col[1] for col in cursor.fetchall()]
                    
                    insert_data = {}
                    for col in cols:
                        if col == "owner_id" and "owner_id" not in body:
                            insert_data[col] = user_session.get("id")
                        elif col == "subscription" and "subscription" not in body and table_name == "users":
                            insert_data[col] = body.get("plan", "free")
                        elif col in body:
                            insert_data[col] = body[col]
                            
                    if "id" in insert_data and insert_data["id"] is None:
                        del insert_data["id"] # Let sqlite autoincrement handle it
                        
                    cols_str = ", ".join(insert_data.keys())
                    placeholders = ", ".join(["?" for _ in insert_data])
                    sql = f"INSERT INTO {table_name} ({cols_str}) VALUES ({placeholders})"
                    
                    last_id, _ = self.db.execute(sql, tuple(insert_data.values()))
                    response_data.append({"id": last_id, "message": "Record inserted successfully"})
                    
                elif action == "UPDATE":
                    # Update fields
                    cursor.execute(f"PRAGMA table_info({table_name});")
                    cols = [col[1] for col in cursor.fetchall()]
                    
                    update_data = {}
                    for col in cols:
                        if col in body and col != "id":
                            update_data[col] = body[col]
                            
                    if update_data:
                        set_clause = ", ".join([f"{k} = ?" for k in update_data.keys()])
                        sql = f"UPDATE {table_name} SET {set_clause}"
                        params = list(update_data.values())
                        
                        if op.conditions and "id = user.id" in op.conditions:
                            sql += " WHERE id = ?"
                            params.append(user_session.get("id"))
                        elif "id" in body:
                            sql += " WHERE id = ?"
                            params.append(body["id"])
                        else:
                            sql += " WHERE id = ?"
                            params.append(user_session.get("id")) # default fallback
                            
                        _, count = self.db.execute(sql, tuple(params))
                        response_data.append({"updated_count": count})
                        
                elif action == "DELETE":
                    sql = f"DELETE FROM {table_name}"
                    params = []
                    if "id" in body:
                        sql += " WHERE id = ?"
                        params.append(body["id"])
                        
                    _, count = self.db.execute(sql, tuple(params))
                    response_data.append({"deleted_count": count})

            # Format Response
            # If it's a list with one item, return it as object, else return full list
            body_res = response_data[0] if len(response_data) == 1 else response_data
            if not response_data and method == "GET":
                body_res = []
            return {"status": 200, "body": body_res}

        except Exception as e:
            return {"status": 500, "body": {"error": f"Database simulation error: {str(e)}"}}

    def _eval_condition(self, condition: str, user_session: Dict[str, Any], body: Dict[str, Any]) -> bool:
        """Evaluates logic gating rules safely."""
        try:
            # 1. Gating rules for Role check
            if "user.role" in condition:
                role = user_session.get("role", "Anonymous")
                # e.g. "user.role != 'Admin'"
                expr = condition.replace("user.role", f"'{role}'")
                return eval(expr, {"__builtins__": None}, {})
                
            # 2. Gating rules for Subscription checks
            if "user.subscription" in condition:
                sub = user_session.get("subscription", "free")
                expr = condition.replace("user.subscription", f"'{sub}'")
                return eval(expr, {"__builtins__": None}, {})

            # 3. Gating rules for db record count limits (e.g. max 3 contacts for free tier)
            if "count(" in condition:
                # E.g., "count(contacts) >= 3"
                import re
                match = re.search(r'count\((\w+)\)', condition)
                if match:
                    table_name = match.group(1)
                    # Query actual count in DB
                    res = self.db.query(f"SELECT COUNT(*) as count FROM {table_name};")
                    count_val = res[0]["count"] if res else 0
                    expr = re.sub(r'count\(\w+\)', str(count_val), condition)
                    return eval(expr, {"__builtins__": None}, {})

            return False
        except Exception:
            return False
