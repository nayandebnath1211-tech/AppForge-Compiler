import json
from pipeline.models import SystemDesign, AppConfig
from pipeline.llm_helper import get_gemini_key, call_gemini_structured, simulate_llm_call

SCHEMA_PROMPT_TEMPLATE = """
You are a systems compiler. Translate the SystemDesign architectural blueprint into a complete, fully-defined AppConfig schema.

SystemDesign Input:
{design_json}

Your compilation must cover:
1. DB Schema (db_schema): Concrete SQL tables, columns (with exact types like INTEGER, TEXT, REAL, BOOLEAN, DATETIME), keys, relations, and indexes.
2. API Schema (api_schema): Complete set of API endpoints, HTTP methods, authorization settings, role permissions, request bodies, and database operations.
3. UI Schema (ui_schema): Pages, routes, layouts, component tree (forms, tables, buttons, stats, charts), and action listeners or API data bindings.
4. Auth Schema (auth_schema): Roles list, exact resource permission mapping, and feature subscription gating rules.
5. Logic Schema (logic_schema): Interceptors or triggers gating API endpoints or UI clicks (e.g., gating database inserts based on contact count and subscription level).

Ensure all names and references are fully aligned between layers (e.g. UI binds to existing APIs; APIs perform operations on existing DB tables).
Conform strictly to the JSON schema output requirement. Do not include markdown code block characters around the raw JSON in the response.
"""

def generate_schemas(design: SystemDesign, api_key: str = None) -> AppConfig:
    """Runs Stage 3 of the compiler pipeline: compiles SystemDesign into concrete AppConfig."""
    has_key = get_gemini_key(api_key) is not None
    
    if has_key:
        design_json = design.model_dump_json(indent=2)
        prompt = SCHEMA_PROMPT_TEMPLATE.format(design_json=design_json)
        try:
            schema_data = call_gemini_structured(prompt, AppConfig, api_key)
            return AppConfig(**schema_data)
        except Exception as e:
            print(f"Gemini API Error in Stage 3: {e}. Falling back to simulation.")
            mock_data = simulate_llm_call(design.app_name, "schema")
            return AppConfig(**mock_data)
    else:
        mock_data = simulate_llm_call(design.app_name, "schema")
        return AppConfig(**mock_data)
