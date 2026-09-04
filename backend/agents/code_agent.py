import os
from typing import TypedDict, List
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import json

from tools.code_tools import check_python_syntax, analyze_python_code

class AgentState(TypedDict):
    code: str
    syntax_valid: bool
    issues: List[str]
    explanation: str
    suggested_fix: str
    improvements: List[str]
    agent_actions: List[str]

def syntax_check_node(state: AgentState):
    state["agent_actions"].append("Checking Python syntax...")
    syntax_result = check_python_syntax(state["code"])
    state["syntax_valid"] = syntax_result["valid"]
    
    if not syntax_result["valid"]:
        error_msg = f"Syntax error: {syntax_result['error']}"
        if syntax_result['line']:
            error_msg += f" on line {syntax_result['line']}"
        state["issues"].append(error_msg)
        
    return state

def should_run_analysis(state: AgentState):
    # Conditional logic based on state
    if state["syntax_valid"]:
        return "static_analysis"
    return "generate_fix"

def static_analysis_node(state: AgentState):
    state["agent_actions"].append("Running code analysis...")
    analysis_issues = analyze_python_code(state["code"])
    state["issues"].extend(analysis_issues)
    return state

def generate_fix_node(state: AgentState):
    state["agent_actions"].append("Generating fix suggestion...")
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        state["explanation"] = "Configuration Error: Missing OPENAI_API_KEY in environment variables."
        return state
        
    try:
        # Use LLM to generate fix and explanation
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        
        prompt = f"""
        You are an AI Code Review & Bug Fixing Agent.
        Review the following Python code.
        
        Code:
        ```python
        {state['code']}
        ```
        
        Syntax Valid: {state['syntax_valid']}
        Known Issues: {state['issues']}
        
        Provide a JSON response with exactly three keys:
        - "explanation": Explain the issues found in simple language.
        - "suggested_fix": Provide the corrected code (as a string). If no fix is needed, return the original code or a slightly improved version.
        - "improvements": A list of strings containing additional improvement suggestions.
        
        Return ONLY valid JSON.
        """
        
        messages = [
            SystemMessage(content="You are an expert AI code reviewer. Always respond in pure JSON without markdown blocks formatting."),
            HumanMessage(content=prompt)
        ]
        
        response = llm.invoke(messages)
        
        try:
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
            
            result = json.loads(content)
            state["explanation"] = result.get("explanation", "No explanation provided.")
            state["suggested_fix"] = result.get("suggested_fix", "")
            state["improvements"] = result.get("improvements", [])
            
        except json.JSONDecodeError:
            state["explanation"] = "Failed to parse LLM response into JSON."
            state["suggested_fix"] = response.content
            
    except Exception as e:
        state["explanation"] = f"LLM API failure: {str(e)}"
        
    return state

def finalize_node(state: AgentState):
    state["agent_actions"].append("Preparing final response...")
    return state

def build_workflow():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("syntax_check", syntax_check_node)
    workflow.add_node("static_analysis", static_analysis_node)
    workflow.add_node("generate_fix", generate_fix_node)
    workflow.add_node("finalize", finalize_node)
    
    workflow.add_edge(START, "syntax_check")
    # Conditional edge from syntax check
    workflow.add_conditional_edges("syntax_check", should_run_analysis, {
        "static_analysis": "static_analysis",
        "generate_fix": "generate_fix"
    })
    
    workflow.add_edge("static_analysis", "generate_fix")
    workflow.add_edge("generate_fix", "finalize")
    workflow.add_edge("finalize", END)
    
    return workflow.compile()
