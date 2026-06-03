import json
from pipeline.models import AppIntent, SystemDesign
from pipeline.llm_helper import get_gemini_key, call_gemini_structured, simulate_llm_call

SYSTEM_DESIGN_PROMPT_TEMPLATE = """
You are a principal systems architect. Translate the structured intermediate AppIntent schema into a concrete SystemDesign architectural blueprint.

AppIntent Input:
{intent_json}

Define:
1. Design Entities: Concrete data models, fields (name, type, required), relationships, and allowed operations per role (read, write, delete).
2. Action Flows: Multi-step workflows detailing what triggers them, the operations they perform, and which entities they touch.
3. Roles: Complete roles mapping.

Conform strictly to the JSON schema output requirement. Do not include markdown code block characters around the raw JSON in the response.
"""

def design_system(intent: AppIntent, api_key: str = None) -> SystemDesign:
    """Runs Stage 2 of the compiler pipeline: converts AppIntent to SystemDesign blueprint."""
    has_key = get_gemini_key(api_key) is not None
    
    if has_key:
        intent_json = intent.model_dump_json(indent=2)
        prompt = SYSTEM_DESIGN_PROMPT_TEMPLATE.format(intent_json=intent_json)
        try:
            design_data = call_gemini_structured(prompt, SystemDesign, api_key)
            return SystemDesign(**design_data)
        except Exception as e:
            print(f"Gemini API Error in Stage 2: {e}. Falling back to simulation.")
            mock_data = simulate_llm_call(intent.description, "design")
            return SystemDesign(**mock_data)
    else:
        mock_data = simulate_llm_call(intent.description, "design")
        return SystemDesign(**mock_data)
