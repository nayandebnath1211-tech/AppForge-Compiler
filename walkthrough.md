# Walkthrough: AppForge Compiler OS

The AppForge Compiler OS is a fully engineered, multi-stage compiler that converts open-ended natural language instructions into strict, validated, and immediately executable application schemas. 

It integrates a cross-layer semantic validation suite, a targeted self-repair loop, and an interactive runtime simulation environment (mock database & router sandbox) that enables live application preview and data entry testing.

## Summary of Completed Tasks

### 1. Compiler Pipeline Stages
- **Stage 1: Intent Extraction** ([intent_extractor.py](file:///c:/Users/Nayan/Desktop/antigravity/compiler/pipeline/intent_extractor.py)): Parses raw product instructions into intermediate intent configurations mapping data entities, roles, and business rules.
- **Stage 2: System Design Layer** ([system_designer.py](file:///c:/Users/Nayan/Desktop/antigravity/compiler/pipeline/system_designer.py)): Structures entity relations, CRUD permissions, action trigger events, and role access matrices.
- **Stage 3: Schema Generation** ([schema_generator.py](file:///c:/Users/Nayan/Desktop/antigravity/compiler/pipeline/schema_generator.py)): Compiles intermediate architectures into type-safe schema files representing DB columns, REST endpoints, UI screens, Auth rules, and interceptors.

### 2. Validation & Repair Engine
- **Cross-Layer Validator** ([validator.py](file:///c:/Users/Nayan/Desktop/antigravity/compiler/pipeline/validator.py)): Performs structural checks across layers, confirming that UI views bind to existing APIs, API actions query existing DB tables, and endpoint/page access corresponds to defined role matrices.
- **Self-Repair Engine** ([repair_engine.py](file:///c:/Users/Nayan/Desktop/antigravity/compiler/pipeline/repair_engine.py)): Analyzes validation errors and executes a correction loop by supplying a targeted correction prompt to resolve inconsistencies without brute re-generation of the entire schema.

### 3. Simulation Sandbox & SQLite Database
- **In-Memory SQLite DB** ([mock_db.py](file:///c:/Users/Nayan/Desktop/antigravity/compiler/runtime/mock_db.py)): Converts DB schema tables and types into real SQL tables in a running database, pre-seeded with sample records.
- **Mock API Router** ([mock_api.py](file:///c:/Users/Nayan/Desktop/antigravity/compiler/runtime/mock_api.py)): Simulates API gateway route resolution, enforces authorization roles, and runs logic gates (e.g., gating record sizes based on subscription tiers).
- **App Simulator Coordinator** ([simulator.py](file:///c:/Users/Nayan/Desktop/antigravity/compiler/runtime/simulator.py)): Runs page rendering, binds components dynamically to real SQLite records, handles form submissions, and logs SQL queries and HTTP logs.

### 4. Interactive Web Dashboard
- **Web App Entry** ([main.py](file:///c:/Users/Nayan/Desktop/antigravity/compiler/main.py)): Starts the Flask server exposing APIs for compiling instructions, routing simulator calls, inspecting SQLite tables in real-time, and running benchmarks.
- **Responsive Dashboard** ([index.html](file:///c:/Users/Nayan/Desktop/antigravity/compiler/web/templates/index.html), [style.css](file:///c:/Users/Nayan/Desktop/antigravity/compiler/web/static/css/style.css), [app.js](file:///c:/Users/Nayan/Desktop/antigravity/compiler/web/static/js/app.js)): Glassmorphism dark-mode control center featuring active pipeline logs, an interactive mock browser sandbox, live SQL grids, and evaluation stats.

---

## Verification Results

### Automated Unit Tests
A suite of 7 unit tests covering schema validators, programmatic repair logic, in-memory SQLite tables, and API logic gates was executed:

```
C:\Users\Nayan\Desktop\antigravity\compiler\pipeline\llm_helper.py:3: FutureWarning: 
All support for the `google.generativeai` package has ended. It will no longer be receiving 
updates or bug fixes. Please switch to the `google.genai` package as soon as possible.
  import google.generativeai as genai
.......
----------------------------------------------------------------------
Ran 7 tests in 0.011s

OK
```

All 7 test cases passed successfully.

---

## Operating Instructions

### Running the Dashboard Locally
1. Start the Flask server:
   ```powershell
   python main.py
   ```
2. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

### Running the Test Suite
To run the automated tests:
```powershell
python -m unittest tests.py
```
