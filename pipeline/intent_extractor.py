import json
from pipeline.models import AppIntent
from pipeline.llm_helper import get_gemini_key, call_gemini_structured, simulate_llm_call

INTENT_PROMPT_TEMPLATE = """
You are a principal system architect. Extract the core application intent from the user's instructions below.

User Instructions:
"{user_instruction}"

Extract and organize this into:
1. Application Name (app_name): Short alphanumeric name.
2. Description: Brief summary.
3. Entities: The core database entities, their fields (name, type, required), and their relationships.
4. User Roles: Allowed roles, their permissions, and whether they are gated.
5. Features: Component modules, auth requirements, role gates, and premium gates.
6. Business Logic Rules: Specific logic boundaries (e.g., limits, access restrictions, pricing rules).

Conform strictly to the JSON schema output requirement. Do not include markdown code block characters around the raw JSON in the response.
"""

def extract_intent(user_instruction: str, api_key: str = None) -> AppIntent:
    """Runs Stage 1 of the compiler pipeline: parses raw prompt to AppIntent intermediate schema."""
    has_key = get_gemini_key(api_key) is not None
    
    if has_key:
        prompt = INTENT_PROMPT_TEMPLATE.format(user_instruction=user_instruction)
        try:
            intent_data = call_gemini_structured(prompt, AppIntent, api_key)
            return AppIntent(**intent_data)
        except Exception as e:
            # Fallback to simulated generator in case of API issues
            print(f"Gemini API Error in Stage 1: {e}. Falling back to simulation.")
            mock_data = simulate_llm_call(user_instruction, "intent")
            return AppIntent(**mock_data)
    else:
        mock_data = simulate_llm_call(user_instruction, "intent")
        return AppIntent(**mock_data)
