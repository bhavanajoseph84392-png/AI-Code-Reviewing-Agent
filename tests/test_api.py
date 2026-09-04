import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add backend to path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.json == {"status": "ok", "service": "AI Code Review Agent API"}

def test_check_syntax_valid(client):
    response = client.post('/api/check-syntax', json={"code": "print('hello')"})
    assert response.status_code == 200
    assert response.json["valid"] == True

def test_check_syntax_invalid(client):
    response = client.post('/api/check-syntax', json={"code": "print('hello'"})
    assert response.status_code == 200
    assert response.json["valid"] == False
    assert "unexpected EOF" in response.json["error"] or "EOF" in response.json["error"] or "never closed" in response.json["error"] or "expected" in response.json["error"]

@patch('agents.code_agent.ChatOpenAI')
def test_analyze_code_valid(mock_chat, client):
    # Set fake API key for test
    os.environ['OPENAI_API_KEY'] = 'fake-key'
    
    mock_instance = MagicMock()
    mock_chat.return_value = mock_instance
    mock_instance.invoke.return_value = MagicMock(content='{"explanation": "Looks good", "suggested_fix": "print(\'hello\')", "improvements": []}')
    
    response = client.post('/api/analyze', json={"code": "print('hello')"})
    assert response.status_code == 200
    assert response.json["syntax_valid"] == True
    assert response.json["explanation"] == "Looks good"
    assert "Checking Python syntax..." in response.json["agent_actions"]

def test_analyze_no_code(client):
    response = client.post('/api/analyze', json={})
    assert response.status_code == 400
