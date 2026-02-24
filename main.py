from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import uuid
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Store code snippets (in production, use a database)
code_snippets = {}

# HTML Template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Python Code Snippet Manager</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            opacity: 0.9;
            font-size: 1.1em;
        }
        
        .main-content {
            padding: 30px;
        }
        
        .input-section {
            margin-bottom: 30px;
        }
        
        .input-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
            font-size: 1.1em;
        }
        
        textarea {
            width: 100%;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 14px;
            resize: vertical;
            transition: border-color 0.3s;
        }
        
        textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .options {
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        
        .option-item {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .option-item input[type="radio"] {
            width: auto;
            margin-right: 5px;
        }
        
        .option-item label {
            display: inline;
            margin-bottom: 0;
            font-weight: normal;
        }
        
        input[type="number"] {
            padding: 8px;
            border: 2px solid #e0e0e0;
            border-radius: 5px;
            width: 80px;
        }
        
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            font-size: 1.1em;
            font-weight: 600;
            border-radius: 10px;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            width: 100%;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
        }
        
        .result-section {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-top: 30px;
        }
        
        .result-section h3 {
            color: #333;
            margin-bottom: 15px;
        }
        
        .url-box {
            background: white;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            word-break: break-all;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 14px;
        }
        
        .code-example {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 8px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 14px;
            overflow-x: auto;
        }
        
        .copy-btn {
            background: #28a745;
            margin-top: 10px;
            padding: 10px;
            font-size: 0.9em;
        }
        
        .copy-btn:hover {
            background: #218838;
        }
        
        .error {
            color: #dc3545;
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
        }
        
        .success {
            color: #28a745;
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
        }
        
        .footer {
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            color: #666;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Python Code Snippet Manager</h1>
            <p>Store your Python code and execute it remotely using exec(requests.get(url).text)</p>
        </div>
        
        <div class="main-content">
            <div class="input-section">
                <div class="input-group">
                    <label for="code">📝 Your Python Code:</label>
                    <textarea id="code" rows="10" placeholder="print('Hello, World!')" required></textarea>
                </div>
                
                <div class="options">
                    <div class="option-item">
                        <input type="radio" name="storage" id="permanent" value="permanent" checked>
                        <label for="permanent">💾 Permanent Storage</label>
                    </div>
                    <div class="option-item">
                        <input type="radio" name="storage" id="temporary" value="temporary">
                        <label for="temporary">⏱️ Temporary Storage</label>
                    </div>
                    <div class="option-item" id="expiryOption" style="display: none;">
                        <label for="expiry">Expires in (minutes):</label>
                        <input type="number" id="expiry" min="1" max="1440" value="60">
                    </div>
                </div>
                
                <button onclick="createSnippet()">🔗 Generate Link</button>
            </div>
            
            <div class="result-section" id="result" style="display: none;">
                <h3>✅ Your Code Link is Ready!</h3>
                <div class="url-box" id="snippetUrl"></div>
                
                <h3>📋 Python Execution Code:</h3>
                <div class="code-example" id="execCode"></div>
                <button class="copy-btn" onclick="copyToClipboard()">📋 Copy to Clipboard</button>
                
                <div id="statusMessage"></div>
            </div>
        </div>
        
        <div class="footer">
            <p>⚡ Use with caution: Only execute code from trusted sources!</p>
        </div>
    </div>

    <script>
        const baseUrl = window.location.origin;
        
        document.querySelectorAll('input[name="storage"]').forEach(radio => {
            radio.addEventListener('change', function() {
                document.getElementById('expiryOption').style.display = 
                    this.value === 'temporary' ? 'flex' : 'none';
            });
        });
        
        async function createSnippet() {
            const code = document.getElementById('code').value.trim();
            if (!code) {
                alert('Please enter some code!');
                return;
            }
            
            const storageType = document.querySelector('input[name="storage"]:checked').value;
            const expiry = storageType === 'temporary' ? 
                parseInt(document.getElementById('expiry').value) : null;
            
            try {
                const response = await fetch('/api/snippets', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        code: code,
                        storage_type: storageType,
                        expiry_minutes: expiry
                    })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    const snippetUrl = `${baseUrl}/snippet/${data.id}`;
                    const execCode = `import requests\\nexec(requests.get('${snippetUrl}').text)`;
                    
                    document.getElementById('snippetUrl').textContent = snippetUrl;
                    document.getElementById('execCode').textContent = execCode;
                    
                    let statusMsg = '';
                    if (storageType === 'temporary') {
                        const expiryTime = new Date(data.expires_at * 1000).toLocaleString();
                        statusMsg = `<div class="success">⏰ This code will expire on: ${expiryTime}</div>`;
                    } else {
                        statusMsg = '<div class="success">💾 This is a permanent link (will not expire)</div>';
                    }
                    
                    document.getElementById('statusMessage').innerHTML = statusMsg;
                    document.getElementById('result').style.display = 'block';
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (error) {
                alert('Error creating snippet: ' + error);
            }
        }
        
        async function copyToClipboard() {
            const execCode = document.getElementById('execCode').textContent;
            try {
                await navigator.clipboard.writeText(execCode);
                alert('✅ Copied to clipboard!');
            } catch (err) {
                alert('❌ Failed to copy');
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/snippets', methods=['POST'])
def create_snippet():
    data = request.json
    code = data.get('code')
    storage_type = data.get('storage_type', 'permanent')
    expiry_minutes = data.get('expiry_minutes')
    
    if not code:
        return jsonify({'error': 'No code provided'}), 400
    
    # Generate unique ID
    snippet_id = str(uuid.uuid4())[:8]
    
    # Calculate expiry if temporary
    expires_at = None
    if storage_type == 'temporary' and expiry_minutes:
        expires_at = (datetime.now() + timedelta(minutes=expiry_minutes)).timestamp()
    
    # Store the snippet
    code_snippets[snippet_id] = {
        'code': code,
        'created_at': datetime.now().timestamp(),
        'expires_at': expires_at,
        'storage_type': storage_type
    }
    
    return jsonify({
        'id': snippet_id,
        'expires_at': expires_at,
        'storage_type': storage_type
    })

@app.route('/snippet/<snippet_id>')
def get_snippet(snippet_id):
    snippet = code_snippets.get(snippet_id)
    
    if not snippet:
        return "Snippet not found", 404
    
    # Check if expired
    if snippet.get('expires_at') and datetime.now().timestamp() > snippet['expires_at']:
        # Remove expired snippet
        del code_snippets[snippet_id]
        return "This snippet has expired", 410
    
    # Return the code as plain text
    return snippet['code'], 200, {'Content-Type': 'text/plain'}

@app.route('/api/snippets/<snippet_id>', methods=['DELETE'])
def delete_snippet(snippet_id):
    if snippet_id in code_snippets:
        del code_snippets[snippet_id]
        return jsonify({'message': 'Snippet deleted'})
    return jsonify({'error': 'Snippet not found'}), 404

# Cleanup expired snippets periodically (you can run this as a background task)
@app.route('/api/cleanup', methods=['POST'])
def cleanup_expired():
    expired = []
    current_time = datetime.now().timestamp()
    
    for snippet_id, snippet in list(code_snippets.items()):
        if snippet.get('expires_at') and current_time > snippet['expires_at']:
            expired.append(snippet_id)
            del code_snippets[snippet_id]
    
    return jsonify({'cleaned': len(expired), 'expired_ids': expired})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
