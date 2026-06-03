from typing import Dict, Any, List
from pipeline.models import AppConfig
from runtime.mock_db import MockDatabase
from runtime.mock_api import MockApiRouter

class AppSimulator:
    """
    Coordinates the active runtime sandbox of a compiled application schema configuration.
    Maintains session states, manages mock DB/API routing connections, fetches page assets,
    and returns UI component outputs bound with query logs.
    """
    def __init__(self, config: AppConfig):
        self.config = config
        self.db = MockDatabase(config.db_schema)
        self.router = MockApiRouter(config.api_schema, config.logic_schema, self.db)
        
        # Default session: User 2 (Member on Free plan)
        self.current_user = {
            "id": 2,
            "email": "member@appforge.com",
            "role": "Member",
            "subscription": "free"
        }
        self.request_logs = []

    def switch_user_session(self, role: str, subscription: str = "free"):
        """Changes the current authenticated session to verify gating and permissions."""
        if role == "Admin":
            self.current_user = {
                "id": 1,
                "email": "admin@appforge.com",
                "role": "Admin",
                "subscription": "premium"
            }
        elif role == "Member":
            self.current_user = {
                "id": 2,
                "email": "member@appforge.com",
                "role": "Member",
                "subscription": subscription
            }
        elif role == "PremiumMember":
            self.current_user = {
                "id": 3,
                "email": "premium@appforge.com",
                "role": "Member",
                "subscription": "premium"
            }
        else: # Guest/Anonymous
            self.current_user = {
                "id": None,
                "email": "guest@appforge.com",
                "role": "Anonymous",
                "subscription": "free"
            }
            
        self.log_action("SESSION", f"Switched user session to: Role={role}, Subscription={subscription}")

    def log_action(self, category: str, message: str, details: Any = None):
        self.request_logs.append({
            "category": category,
            "message": message,
            "details": details
        })

    def get_rendered_page(self, route: str) -> Dict[str, Any]:
        """
        Renders a page by evaluating auth permissions, executing API bindings, 
        and assembling the UI component tree with database data.
        """
        page = None
        for p in self.config.ui_schema.pages:
            if p.route == route:
                page = p
                break
                
        if not page:
            return {"status": 404, "error": f"Page at route '{route}' not found."}

        # Check Page Gate permissions
        if page.auth_required:
            if not self.current_user.get("id"):
                self.log_action("UI_GATE", f"Blocked access to page '{page.name}' ({route}): Auth required.")
                return {"status": 401, "error": "Unauthorized: Page requires login."}
                
            role = self.current_user.get("role", "Anonymous")
            if page.allowed_roles and role not in page.allowed_roles:
                self.log_action("UI_GATE", f"Blocked access to page '{page.name}' ({route}): Role '{role}' not allowed.")
                return {"status": 403, "error": f"Forbidden: Page restricted."}

        self.log_action("NAVIGATE", f"Rendered page: '{page.name}' ({route})")
        
        rendered_components = []
        for comp in page.components:
            comp_data = comp.model_dump()
            
            # Execute and inject API Bindings if present
            if comp.api_binding:
                binding = comp.api_binding
                self.log_action("API_BIND", f"Component '{comp.id}' fetching data via {binding.method} {binding.path}")
                
                res = self.router.handle_request(
                    path=binding.path,
                    method=binding.method,
                    user_session=self.current_user
                )
                
                # Log HTTP status
                status = res.get("status", 500)
                body = res.get("body", {})
                self.log_action("API_RESPONSE", f"{binding.method} {binding.path} returned status {status}", body)
                
                if status == 200:
                    comp_data["props"][binding.bind_to] = body
                else:
                    comp_data["props"][binding.bind_to] = []
                    comp_data["props"]["error"] = body.get("error", "Failed to fetch data.")
            
            rendered_components.append(comp_data)

        return {
            "status": 200,
            "page_name": page.name,
            "layout": page.layout,
            "components": rendered_components,
            "current_user": self.current_user
        }

    def execute_action(self, route: str, component_id: str, action_index: int, action_payload: Dict[str, Any] = None) -> Dict[str, Any]:
        """Triggers a UI event action (e.g. form submit or button click) and returns results."""
        # Find page & component
        page = None
        for p in self.config.ui_schema.pages:
            if p.route == route:
                page = p
                break
                
        if not page:
            return {"status": 404, "error": "Page not found"}
            
        component = None
        for c in page.components:
            if c.id == component_id:
                component = c
                break
                
        if not component:
            return {"status": 404, "error": "Component not found"}
            
        if action_index >= len(component.actions):
            return {"status": 400, "error": "Action index out of range"}
            
        action = component.actions[action_index]
        self.log_action("UI_ACTION", f"Component '{component_id}' triggered {action.trigger} -> {action.action_type}")
        
        if action.action_type == "navigate":
            return {
                "action_type": "navigate",
                "target": action.target,
                "status": 200
            }
            
        elif action.action_type == "api_call":
            method = "GET"
            if action.payload and "method" in action.payload:
                method = action.payload["method"].upper()
                
            res = self.router.handle_request(
                path=action.target,
                method=method,
                body=action_payload,
                user_session=self.current_user
            )
            
            status = res.get("status", 500)
            body = res.get("body", {})
            self.log_action("API_RESPONSE", f"{method} {action.target} returned status {status}", body)
            
            # Special logic check: if updating premium plan, update user session
            if status == 200 and action.target == "/api/subscription/upgrade" and method == "POST":
                self.current_user["subscription"] = "premium"
                # Update sqlite row
                self.db.execute("UPDATE users SET subscription = 'premium' WHERE id = ?;", (self.current_user["id"],))
                self.log_action("SESSION", "User subscription upgraded to premium in database.")
                
            return {
                "action_type": "api_call",
                "status": status,
                "body": body
            }
            
        return {"status": 400, "error": f"Unknown action type: {action.action_type}"}

    def close(self):
        self.db.close()
