from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import uuid
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Permanent storage - kabhi delete nahi hoga
snippets = {}  # id: {code, created_at}

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Permanent Snippet Manager</title>
    <style>
        body {
            font-family: 'Segoe UI', Arial;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            margin: 0;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        h1 {
            text-align: center;
            color: #667eea;
            margin-bottom: 30px;
        }
        
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 10px;
        }
        
        .tab {
            padding: 10px 20px;
            cursor: pointer;
            border-radius: 8px 8px 0 0;
            font-weight: 600;
        }
        
        .tab.active {
            background: #667eea;
            color: white;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        textarea {
            width: 100%;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-family: monospace;
            font-size: 14px;
            margin: 10px 0;
            resize: vertical;
        }
        
        button {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 8px;
            font-size: 1em;
            cursor: pointer;
            margin: 5px;
        }
        
        button:hover {
            background: #764ba2;
        }
        
        .snippet {
            background: #f8f9fa;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
        }
        
        .snippet-id {
            color: #667eea;
            font-weight: bold;
            font-family: monospace;
            font-size: 1.2em;
        }
        
        .snippet-preview {
            color: #666;
            margin: 10px 0;
            font-family: monospace;
        }
        
        .snippet-actions {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .result-box {
            background: #f0f2f5;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            display: none;
        }
        
        .url-box {
            background: white;
            padding: 15px;
            border: 2px solid #667eea;
            border-radius: 8px;
            word-break: break-all;
            font-family: monospace;
        }
        
        .code-box {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 8px;
            font-family: monospace;
            overflow-x: auto;
        }
        
        .search-box {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            margin: 10px 0;
            font-size: 1em;
        }
        
        .stats {
            display: flex;
            gap: 20px;
            justify-content: center;
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }
        
        .stat-item {
            text-align: center;
        }
        
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        
        .footer {
            margin-top: 40px;
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
        }
        
        .footer a {
            color: white;
            text-decoration: none;
            margin: 0 10px;
        }
        
        .footer a:hover {
            text-decoration: underline;
        }
        
        .delete-btn {
            background: #dc3545;
        }
        
        .delete-btn:hover {
            background: #c82333;
        }
        
        .edit-btn {
            background: #28a745;
        }
        
        .edit-btn:hover {
            background: #218838;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Permanent Python Snippet Manager</h1>
        <p style="text-align: center;">No Login Required | Permanent Storage | Never Deletes</p>
        
        <!-- Stats -->
        <div class="stats">
            <div class="stat-item">
                <div class="stat-value" id="totalSnippets">0</div>
                <div>Total Snippets</div>
            </div>
        </div>
        
        <!-- Tabs -->
        <div class="tabs">
            <div class="tab active" onclick="switchTab('create')">📝 Create New</div>
            <div class="tab" onclick="switchTab('view')">👁️ View All</div>
            <div class="tab" onclick="switchTab('search')">🔍 Search</div>
        </div>
        
        <!-- Create Tab -->
        <div id="createTab" class="tab-content active">
            <h3>Create New Snippet</h3>
            <textarea id="code" rows="8" placeholder="print('Hello, World!')"></textarea>
            <button onclick="createSnippet()">🔗 Generate Permanent Link</button>
        </div>
        
        <!-- View All Tab -->
        <div id="viewTab" class="tab-content">
            <h3>All Snippets (Permanent)</h3>
            <div id="snippetList"></div>
            <button onclick="loadSnippets()" style="margin-top: 10px;">🔄 Refresh</button>
        </div>
        
        <!-- Search Tab -->
        <div id="searchTab" class="tab-content">
            <h3>Search Snippets</h3>
            <input type="text" id="searchInput" class="search-box" placeholder="Type to search..." onkeyup="searchSnippets()">
            <div id="searchResults"></div>
        </div>
        
        <!-- Result Section -->
        <div id="result" class="result-box">
            <h3>✅ Link Generated (Permanent)</h3>
            <p><strong>Your URL:</strong></p>
            <div class="url-box" id="snippetUrl"></div>
            
            <p><strong>Python Code to Execute:</strong></p>
            <div class="code-box" id="execCode"></div>
            
            <button onclick="copyToClipboard()">📋 Copy Code</button>
        </div>
        
        <!-- Footer with Contact Info -->
        <div class="footer">
            <p>
                <a href="https://t.me/Aotpy" target="_blank">📱 Telegram: @Aotpy</a> | 
                <a href="https://t.me/ObitoStuffs" target="_blank">📢 Channel: @ObitoStuffs</a>
            </p>
            <p>
                <a href="https://Aotpy.vercel.app" target="_blank">🌐 Portfolio</a>
            </p>
            <p style="font-size: 0.8em; margin-top: 10px;">
                ⚠️ Use with caution | All snippets are permanent
            </p>
        </div>
    </div>

    <script>
        const baseUrl = window.location.origin;
        
        // Load on start
        window.onload = function() {
            loadSnippets();
            updateStats();
        };
        
        // Tab switching
        function switchTab(tab) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            if (tab === 'create') {
                document.querySelectorAll('.tab')[0].classList.add('active');
                document.getElementById('createTab').classList.add('active');
            } else if (tab === 'view') {
                document.querySelectorAll('.tab')[1].classList.add('active');
                document.getElementById('viewTab').classList.add('active');
                loadSnippets();
            } else {
                document.querySelectorAll('.tab')[2].classList.add('active');
                document.getElementById('searchTab').classList.add('active');
            }
        }
        
        // Create snippet
        async function createSnippet() {
            const code = document.getElementById('code').value.trim();
            if (!code) {
                alert('Please enter some code!');
                return;
            }
            
            try {
                const response = await fetch('/api/snippets', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ code: code })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    const snippetUrl = `${baseUrl}/snippet/${data.id}`;
                    const execCode = `import requests\\nexec(requests.get('${snippetUrl}').text)`;
                    
                    document.getElementById('snippetUrl').textContent = snippetUrl;
                    document.getElementById('execCode').textContent = execCode;
                    document.getElementById('result').style.display = 'block';
                    
                    // Clear input
                    document.getElementById('code').value = '';
                    
                    // Update stats and lists
                    updateStats();
                    loadSnippets();
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (error) {
                alert('Error: ' + error);
            }
        }
        
        // Load all snippets
        async function loadSnippets() {
            try {
                const response = await fetch('/api/all-snippets');
                const snippets = await response.json();
                
                const list = document.getElementById('snippetList');
                list.innerHTML = '';
                
                if (snippets.length === 0) {
                    list.innerHTML = '<p>No snippets yet. Create one!</p>';
                    return;
                }
                
                // Show latest first
                snippets.reverse().forEach(snippet => {
                    const div = createSnippetElement(snippet);
                    list.appendChild(div);
                });
                
                updateStats();
            } catch (error) {
                console.error('Error:', error);
            }
        }
        
        // Create snippet element
        function createSnippetElement(snippet) {
            const div = document.createElement('div');
            div.className = 'snippet';
            
            const date = new Date(snippet.created_at * 1000).toLocaleString();
            const preview = snippet.preview || snippet.code.substring(0, 100) + '...';
            
            div.innerHTML = `
                <div>
                    <span class="snippet-id">${snippet.id}</span>
                    <small style="float: right;">${date}</small>
                </div>
                <div class="snippet-preview">${preview}</div>
                <div class="snippet-actions">
                    <button onclick="viewSnippet('${snippet.id}')">👁️ View</button>
                    <button class="edit-btn" onclick="editSnippet('${snippet.id}')">✏️ Edit</button>
                    <button class="delete-btn" onclick="deleteSnippet('${snippet.id}')">🗑️ Delete</button>
                    <button onclick="copyUrl('${snippet.id}')">🔗 Copy URL</button>
                </div>
            `;
            
            return div;
        }
        
        // Search snippets
        async function searchSnippets() {
            const query = document.getElementById('searchInput').value.toLowerCase();
            
            const response = await fetch('/api/all-snippets');
            const snippets = await response.json();
            
            const results = document.getElementById('searchResults');
            results.innerHTML = '';
            
            const filtered = snippets.filter(s => 
                s.code.toLowerCase().includes(query) || 
                s.id.toLowerCase().includes(query)
            );
            
            if (filtered.length === 0) {
                results.innerHTML = '<p>No snippets found</p>';
                return;
            }
            
            filtered.reverse().forEach(snippet => {
                const div = createSnippetElement(snippet);
                results.appendChild(div);
            });
        }
        
        // View snippet
        function viewSnippet(id) {
            window.open(`/snippet/${id}`, '_blank');
        }
        
        // Edit snippet
        async function editSnippet(id) {
            const newCode = prompt('Edit your code:');
            if (!newCode) return;
            
            try {
                const response = await fetch(`/api/snippets/${id}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ code: newCode })
                });
                
                if (response.ok) {
                    alert('✅ Snippet updated!');
                    loadSnippets();
                    updateStats();
                } else {
                    alert('Error updating');
                }
            } catch (error) {
                alert('Error: ' + error);
            }
        }
        
        // Delete snippet
        async function deleteSnippet(id) {
            if (!confirm('Are you sure? This will permanently delete the snippet.')) return;
            
            try {
                const response = await fetch(`/api/snippets/${id}`, {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    alert('✅ Snippet deleted');
                    loadSnippets();
                    updateStats();
                } else {
                    alert('Error deleting');
                }
            } catch (error) {
                alert('Error: ' + error);
            }
        }
        
        // Copy URL
        function copyUrl(id) {
            const url = `${baseUrl}/snippet/${id}`;
            navigator.clipboard.writeText(url);
            alert('✅ URL copied!');
        }
        
        // Copy to clipboard
        async function copyToClipboard() {
            const text = document.getElementById('execCode').textContent;
            await navigator.clipboard.writeText(text);
            alert('✅ Copied!');
        }
        
        // Update stats
        async function updateStats() {
            const response = await fetch('/api/all-snippets');
            const snippets = await response.json();
            document.getElementById('totalSnippets').textContent = snippets.length;
        }
    </script>
</body>
</html>
"""

# ========== API ROUTES ==========

@app.route('/')
def home():
    return render_template_string(HTML)

# Create snippet
@app.route('/api/snippets', methods=['POST'])
def create_snippet():
    data = request.json
    code = data.get('code', '').strip()
    
    if not code:
        return jsonify({'error': 'No code provided'}), 400
    
    # Generate unique ID
    snippet_id = str(uuid.uuid4())[:8]
    
    # Store permanently
    snippets[snippet_id] = {
        'id': snippet_id,
        'code': code,
        'created_at': datetime.now().timestamp(),
        'preview': code[:100] + '...' if len(code) > 100 else code
    }
    
    return jsonify({'id': snippet_id})

# Get all snippets
@app.route('/api/all-snippets', methods=['GET'])
def get_all_snippets():
    return jsonify(list(snippets.values()))

# Update snippet
@app.route('/api/snippets/<snippet_id>', methods=['PUT'])
def update_snippet(snippet_id):
    if snippet_id not in snippets:
        return jsonify({'error': 'Not found'}), 404
    
    data = request.json
    new_code = data.get('code', '').strip()
    
    if not new_code:
        return jsonify({'error': 'No code provided'}), 400
    
    # Update
    snippets[snippet_id]['code'] = new_code
    snippets[snippet_id]['preview'] = new_code[:100] + '...' if len(new_code) > 100 else new_code
    
    return jsonify({'success': True})

# Delete snippet
@app.route('/api/snippets/<snippet_id>', methods=['DELETE'])
def delete_snippet(snippet_id):
    if snippet_id in snippets:
        del snippets[snippet_id]
        return jsonify({'success': True})
    return jsonify({'error': 'Not found'}), 404

# Get single snippet (public)
@app.route('/snippet/<snippet_id>')
def get_snippet(snippet_id):
    if snippet_id in snippets:
        return snippets[snippet_id]['code']
    return "Snippet not found", 404

if __name__ == '__main__':
    print("="*50)
    print("✅ Permanent Snippet Manager")
    print("📍 Open: http://localhost:5000")
    print("📝 No login required - All snippets permanent")
    print("="*50)
    app.run(debug=True, port=5000)
