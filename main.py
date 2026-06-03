import os
import sys
import json
from flask import Flask, render_template, jsonify, request
from pipeline.compiler import compile_instruction
from runtime.simulator import AppSimulator
from evaluation.evaluator import AppForgeEvaluator
from pipeline.models import AppConfig

app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(__file__), "web", "templates"),
            static_folder=os.path.join(os.path.dirname(__file__), "web", "static"))

# In-memory storage for active compilation and simulator
active_simulator = None
active_config = None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/compile", methods=["POST"])
def api_compile():
    global active_simulator, active_config
    data = request.json or {}
    prompt = data.get("prompt", "")
    api_key = data.get("api_key", None)
    
    if not prompt.strip():
        return jsonify({"error": "Prompt cannot be empty"}), 400
        
    try:
        result = compile_instruction(prompt, api_key)
        active_config = result["config"]
        
        # Instantiate sandbox simulation with compiled config
        if active_simulator:
            active_simulator.close()
            
        active_simulator = AppSimulator(active_config)
        
        # Format the response
        response = {
            "config": active_config.model_dump(),
            "errors": result["errors"],
            "metadata": result["metadata"]
        }
        return jsonify(response)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Compilation failed: {str(e)}"}), 500

@app.route("/api/simulator/user", methods=["POST"])
def simulator_user():
    global active_simulator
    if not active_simulator:
        return jsonify({"error": "No active simulator. Compile a schema first."}), 400
        
    data = request.json or {}
    role = data.get("role", "Member")
    subscription = data.get("subscription", "free")
    
    active_simulator.switch_user_session(role, subscription)
    return jsonify({"status": "success", "user": active_simulator.current_user})

@app.route("/api/simulator/page", methods=["GET"])
def simulator_page():
    global active_simulator
    if not active_simulator:
        return jsonify({"error": "No active simulator"}), 400
        
    route = request.args.get("route", "/dashboard")
    page_data = active_simulator.get_rendered_page(route)
    return jsonify(page_data)

@app.route("/api/simulator/action", methods=["POST"])
def simulator_action():
    global active_simulator
    if not active_simulator:
        return jsonify({"error": "No active simulator"}), 400
        
    data = request.json or {}
    route = data.get("route", "")
    component_id = data.get("component_id", "")
    action_index = data.get("action_index", 0)
    payload = data.get("payload", {})
    
    res = active_simulator.execute_action(route, component_id, action_index, payload)
    return jsonify(res)

@app.route("/api/simulator/logs", methods=["GET"])
def simulator_logs():
    global active_simulator
    if not active_simulator:
        return jsonify({"logs": []})
        
    return jsonify({"logs": active_simulator.request_logs})

@app.route("/api/simulator/db-inspect", methods=["GET"])
def simulator_db_inspect():
    global active_simulator
    if not active_simulator:
        return jsonify({"tables": {}})
        
    try:
        db = active_simulator.db
        cursor = db.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence';")
        tables = [row[0] for row in cursor.fetchall()]
        
        db_contents = {}
        for table in tables:
            cursor.execute(f"SELECT * FROM {table};")
            rows = [dict(row) for row in cursor.fetchall()]
            db_contents[table] = rows
            
        return jsonify({"tables": db_contents})
    except Exception as e:
        return jsonify({"error": f"DB Inspect failed: {str(e)}"}), 500

@app.route("/api/evaluate", methods=["POST"])
def run_eval():
    data = request.json or {}
    api_key = data.get("api_key", None)
    
    try:
        evaluator = AppForgeEvaluator(api_key)
        report = evaluator.run_evaluation()
        return jsonify(report)
    except Exception as e:
        return jsonify({"error": f"Evaluation failed: {str(e)}"}), 500

@app.route("/api/evaluate/results", methods=["GET"])
def eval_results():
    results_path = os.path.join(os.path.dirname(__file__), "evaluation", "results", "eval_latest.json")
    if not os.path.exists(results_path):
        # Trigger an initial quick evaluation in mock mode to seed the report file
        try:
            evaluator = AppForgeEvaluator()
            report = evaluator.run_evaluation()
            return jsonify(report)
        except Exception as e:
            return jsonify({"error": f"Failed to initialize evaluation results: {str(e)}"}), 500
            
    try:
        with open(results_path, "r") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": f"Failed to read results: {str(e)}"}), 500

if __name__ == "__main__":
    # Ensure templates and static dirs exist
    os.makedirs(os.path.join("web", "templates"), exist_ok=True)
    os.makedirs(os.path.join("web", "static", "css"), exist_ok=True)
    os.makedirs(os.path.join("web", "static", "js"), exist_ok=True)
    
    print("Starting AppForge Flask server on port 5000...")
    app.run(host="0.0.0.0", port=5000, debug=True)
