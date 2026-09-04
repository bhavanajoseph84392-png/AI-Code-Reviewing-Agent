import React, { useState } from 'react';
import './App.css';

function App() {
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const analyzeCode = async () => {
    if (!code.trim()) {
      setError('Please enter some Python code.');
      return;
    }
    
    setLoading(true);
    setError(null);
    setResult(null);
    
    try {
      const response = await fetch('http://localhost:5001/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code })
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Server error occurred');
      }
      
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const clearCode = () => {
    setCode('');
    setResult(null);
    setError(null);
  };

  return (
    <div className="container">
      <header>
        <h1>AI Code Review & Bug Fixing Agent</h1>
        <p>An intelligent agent that analyzes your Python code using AST and LLM to detect bugs, syntax errors, and suggest fixes.</p>
      </header>

      <main>
        <div className="editor-section">
          <textarea 
            value={code} 
            onChange={(e) => setCode(e.target.value)}
            placeholder="Paste your Python code here..."
            spellCheck="false"
          />
          <div className="actions">
            <button onClick={analyzeCode} disabled={loading} className="btn-primary">
              {loading ? 'Analyzing...' : 'Analyze Code'}
            </button>
            <button onClick={clearCode} disabled={loading} className="btn-secondary">
              Clear
            </button>
          </div>
        </div>

        {error && (
          <div className="error-box">
            <strong>Error:</strong> {error}
          </div>
        )}

        {result && (
          <div className="results-section">
            <h2>Agent Results</h2>
            
            <div className="agent-activity">
              <h3>Agent Activity</h3>
              <ul>
                {result.agent_actions.map((action, i) => (
                  <li key={i}>- {action}</li>
                ))}
              </ul>
            </div>

            <div className={`status-box ${result.syntax_valid ? 'valid' : 'invalid'}`}>
              <h3>Syntax Status</h3>
              <p>{result.syntax_valid ? 'Status: Syntax is valid' : 'Status: Syntax error detected'}</p>
            </div>

            {result.issues && result.issues.length > 0 && (
              <div className="issues-box">
                <h3>Issues Found</h3>
                <ul>
                  {result.issues.map((issue, i) => (
                    <li key={i}>{issue}</li>
                  ))}
                </ul>
              </div>
            )}

            <div className="explanation-box">
              <h3>Explanation</h3>
              <p>{result.explanation}</p>
            </div>

            {result.suggested_fix && (
              <div className="fix-box">
                <h3>Suggested Fix</h3>
                <pre><code>{result.suggested_fix}</code></pre>
              </div>
            )}

            {result.improvements && result.improvements.length > 0 && (
              <div className="improvements-box">
                <h3>Improvements</h3>
                <ul>
                  {result.improvements.map((imp, i) => (
                    <li key={i}>{imp}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
