from flask import Blueprint, request, jsonify
from agents.code_agent import build_workflow

analyze_bp = Blueprint('analyze', __name__)
workflow = build_workflow()

@analyze_bp.route('/check-syntax', methods=['POST'])
def check_syntax():
    data = request.json
    if not data or 'code' not in data:
        return jsonify({"error": "No code provided"}), 400
        
    code = data['code']
    
    # Run only syntax check part via tools for direct checking
    from tools.code_tools import check_python_syntax
    result = check_python_syntax(code)
    
    return jsonify(result), 200

@analyze_bp.route('/analyze', methods=['POST'])
def analyze_code():
    data = request.json
    if not data or 'code' not in data:
        return jsonify({"error": "No code provided"}), 400
        
    code = data['code']
    
    # Initialize state
    initial_state = {
        "code": code,
        "syntax_valid": True,
        "issues": [],
        "explanation": "",
        "suggested_fix": "",
        "improvements": [],
        "agent_actions": []
    }
    
    # Run graph
    try:
        result = workflow.invoke(initial_state)
        
        # Clean up output format
        response = {
            "syntax_valid": result["syntax_valid"],
            "issues": result["issues"],
            "explanation": result["explanation"],
            "suggested_fix": result["suggested_fix"],
            "improvements": result["improvements"],
            "agent_actions": result["agent_actions"]
        }
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
