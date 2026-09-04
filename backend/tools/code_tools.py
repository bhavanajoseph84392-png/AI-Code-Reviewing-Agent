import ast

def check_python_syntax(code: str) -> dict:
    """
    Checks if the provided Python code has syntax errors.
    Returns a dictionary with 'valid', 'error', and 'line'.
    """
    try:
        ast.parse(code)
        return {"valid": True, "error": None, "line": None}
    except SyntaxError as e:
        return {
            "valid": False, 
            "error": str(e.msg), 
            "line": e.lineno
        }
    except Exception as e:
        return {
            "valid": False, 
            "error": str(e), 
            "line": None
        }

def analyze_python_code(code: str) -> list:
    """
    Performs basic static analysis on Python code using AST.
    Finds simple issues like 'eval' usage, lack of docstrings, etc.
    """
    issues = []
    try:
        tree = ast.parse(code)
        
        # Check for module docstring
        if not ast.get_docstring(tree):
            issues.append("Consider adding a module-level docstring.")
            
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not ast.get_docstring(node):
                    issues.append(f"Function '{node.name}' is missing a docstring.")
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == 'eval':
                    issues.append("Warning: Avoid using 'eval' as it can execute arbitrary code.")
                    
    except Exception:
        # Ignore parse errors here as they are caught by syntax check
        pass
        
    return issues
