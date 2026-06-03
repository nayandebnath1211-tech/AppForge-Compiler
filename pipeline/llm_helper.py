import os
import json
import google.generativeai as genai
from pipeline.models import AppIntent, AppConfig
from evaluation.dataset import ALL_PROMPTS, get_prebuilt_mock_schema

def get_gemini_key(user_provided_key=None):
    """Retrieves the API key checking parameters, environment, or dotenv file."""
    if user_provided_key and user_provided_key.strip():
        return user_provided_key.strip()
    
    # Check env variables
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key
        
    return None

def call_gemini_structured(prompt: str, response_model, api_key: str = None) -> dict:
    """
    Calls the Gemini API using structured JSON output.
    Returns the parsed JSON dictionary.
    """
    key = get_gemini_key(api_key)
    if not key:
        raise ValueError("Gemini API Key not configured. Please supply an API key.")

    genai.configure(api_key=key)
    # Use standard gemini-1.5-flash
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Set up generation config for structured output
    config = genai.types.GenerationConfig(
        response_mime_type="application/json",
        response_schema=response_model,
        temperature=0.1  # low temperature for maximum determinism
    )
    
    response = model.generate_content(prompt, generation_config=config)
    
    try:
        # The output is guaranteed to be JSON matching the response_model schema
        data = json.loads(response.text)
        return data
    except Exception as e:
        # Fallback in case parsing fails
        import re
        json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        raise RuntimeError(f"Failed to parse LLM structured response: {e}. Raw content: {response.text}")

def simulate_llm_call(prompt_text: str, stage: str) -> dict:
    """
    Simulates LLM response for demonstration when no key is set.
    Looks up the nearest dataset match or falls back to a generic schema.
    """
    # Normalize prompt to find match
    matched_id = None
    prompt_text_lower = prompt_text.lower().strip()
    
    for item in ALL_PROMPTS:
        if item["prompt"].lower().strip() in prompt_text_lower or prompt_text_lower in item["prompt"].lower().strip():
            matched_id = item["id"]
            break
            
    if not matched_id:
        # Guess matching prompt based on keywords
        if "crm" in prompt_text_lower:
            matched_id = "prod-1"
        elif "shop" in prompt_text_lower or "e-commerce" in prompt_text_lower:
            matched_id = "prod-2"
        elif "trello" in prompt_text_lower or "task" in prompt_text_lower:
            matched_id = "prod-3"
        elif "ticket" in prompt_text_lower or "support" in prompt_text_lower:
            matched_id = "prod-4"
        elif "hotel" in prompt_text_lower or "booking" in prompt_text_lower:
            matched_id = "prod-5"
        else:
            matched_id = "generic"
            
    # Mocking different pipeline stages
    if stage == "intent":
        if matched_id == "prod-1":
            return {
                "app_name": "SleekCRM",
                "description": "Customer Relationship Manager with dashboard, contacts and billing gating.",
                "entities": [
                    {"name": "contacts", "fields": [
                        {"name": "name", "type": "string", "required": True},
                        {"name": "email", "type": "string", "required": True},
                        {"name": "phone", "type": "string", "required": False},
                        {"name": "company", "type": "string", "required": False}
                    ], "relationships": ["belongs_to users"]},
                    {"name": "deals", "fields": [
                        {"name": "title", "type": "string", "required": True},
                        {"name": "amount", "type": "float", "required": True},
                        {"name": "stage", "type": "string", "required": True}
                    ], "relationships": ["belongs_to contacts"]}
                ],
                "roles": [
                    {"role_name": "Admin", "permissions": ["contacts:read", "contacts:write", "analytics:read"], "is_premium_restricted": False},
                    {"role_name": "Member", "permissions": ["contacts:read", "contacts:write"], "is_premium_restricted": False}
                ],
                "features": [
                    {"name": "Contacts Management", "description": "Add and view contacts", "requires_auth": True},
                    {"name": "Sales Analytics", "description": "Analyze deals amount and status", "requires_auth": True, "gated_by_role": "Admin"},
                    {"name": "Premium Gating", "description": "Limit contacts for free tier", "requires_auth": True, "gated_by_subscription": "premium"}
                ],
                "business_logic_rules": [
                    "Only Admin can see analytics page",
                    "Limit contacts to 3 for non-premium users"
                ]
            }
        else:
            return {
                "app_name": "SimulatedApp",
                "description": "Simulated description for: " + prompt_text[:50],
                "entities": [
                    {"name": "items", "fields": [{"name": "name", "type": "string", "required": True}], "relationships": []}
                ],
                "roles": [
                    {"role_name": "Admin", "permissions": ["items:read", "items:write"], "is_premium_restricted": False},
                    {"role_name": "Member", "permissions": ["items:read"], "is_premium_restricted": False}
                ],
                "features": [
                    {"name": "Items Viewer", "description": "View lists", "requires_auth": True}
                ],
                "business_logic_rules": []
            }
            
    elif stage == "design":
        if matched_id == "prod-1":
            return {
                "app_name": "SleekCRM",
                "entities": [
                    {
                        "name": "contacts",
                        "description": "Stores user CRM leads",
                        "fields": [
                            {"name": "name", "type": "string", "required": True},
                            {"name": "email", "type": "string", "required": True},
                            {"name": "phone", "type": "string", "required": False},
                            {"name": "company", "type": "string", "required": False}
                        ],
                        "relationships": ["belongs_to users"],
                        "allowed_operations": {"read": ["Admin", "Member"], "write": ["Admin", "Member"]}
                    },
                    {
                        "name": "deals",
                        "description": "Sales opportunities",
                        "fields": [
                            {"name": "title", "type": "string", "required": True},
                            {"name": "amount", "type": "float", "required": True},
                            {"name": "stage", "type": "string", "required": True}
                        ],
                        "relationships": ["belongs_to contacts"],
                        "allowed_operations": {"read": ["Admin", "Member"], "write": ["Admin"]}
                    }
                ],
                "flows": [
                    {"name": "Add Contact", "trigger": "user click submit", "steps": ["validate contact details", "insert contact in DB", "reload list"], "affected_entities": ["contacts"]},
                    {"name": "Upgrade Plan", "trigger": "user upgrade billing", "steps": ["run payment mock", "update subscription field in users table"], "affected_entities": ["users"]}
                ],
                "roles": [
                    {"role_name": "Admin", "permissions": ["contacts:read", "contacts:write", "analytics:read"], "is_premium_restricted": False},
                    {"role_name": "Member", "permissions": ["contacts:read", "contacts:write"], "is_premium_restricted": False}
                ]
            }
        else:
            return {
                "app_name": "SimulatedApp",
                "entities": [
                    {
                        "name": "items",
                        "description": "Standard tracking item",
                        "fields": [{"name": "name", "type": "string", "required": True}],
                        "relationships": [],
                        "allowed_operations": {"read": ["Admin", "Member"], "write": ["Admin"]}
                    }
                ],
                "flows": [],
                "roles": [
                    {"role_name": "Admin", "permissions": ["items:read", "items:write"], "is_premium_restricted": False},
                    {"role_name": "Member", "permissions": ["items:read"], "is_premium_restricted": False}
                ]
            }
            
    elif stage == "schema":
        # Returns the full prebuilt schema structure matching AppConfig
        return get_prebuilt_mock_schema(matched_id)
        
    return {}
