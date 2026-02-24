from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import uuid
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# JSON file for permanent storage
DATA_FILE = 'snippets.json'

# Ensure snippets.json exists
def ensure_json_file():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump({}, f)
        print(f"✅ Created new {DATA_FILE} file")
    else:
        print(f"📁 {DATA_FILE} already exists")

# Load snippets from JSON file
def load_snippets():
    ensure_json_file()
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Error loading JSON: {e}")
        return {}

# Save snippets to JSON file
def save_snippets(snippets):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(snippets, f, indent=2)
        print(f"💾 Saved to {DATA_FILE}")
    except Exception as e:
        print(f"❌ Error saving: {e}")

# Initialize snippets from file
snippets = load_snippets()

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Permanent JSON Snippet Manager</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 10px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        @media (min-width: 768px) {
            .container { padding: 30px; }
        }
        
        h1 {
            text-align: center;
            color: #667eea;
            font-size: 24px;
            margin-bottom: 5px;
        }
        
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 20px;
            font-size: 14px;
        }
        
        .json-badge {
            background: #28a745;
            color: white;
            padding: 5px 15px;
            border-radius: 50px;
            display: inline-block;
            margin: 0 auto 20px;
            text-align: center;
            font-size: 14px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-bottom: 20px;
        }
        
        @media (min-width: 768px) {
            .stats-grid {
                grid-template-columns: repeat(4, 1fr);
            }
        }
        
        .stat-card {
            background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%);
            padding: 15px 10px;
            border-radius: 12px;
            text-align: center;
        }
        
        .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
        }
        
        .stat-label {
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }
        
        .tabs {
            display: flex;
            overflow-x: auto;
            gap: 5px;
            margin-bottom: 20px;
            padding-bottom: 5px;
            -webkit-overflow-scrolling: touch;
        }
        
        .tab {
            padding: 10px 15px;
            background: #f0f2f5;
            border-radius: 25px;
            font-size: 14px;
            font-weight: 600;
            white-space: nowrap;
            cursor: pointer;
            transition: all 0.3s;
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
            border-radius: 12px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            resize: vertical;
            min-height: 150px;
            margin-bottom: 15px;
        }
        
        .file-upload-area {
            border: 2px dashed #667eea;
            border-radius: 12px;
            padding: 30px 20px;
            text-align: center;
            background: #f8f9fa;
            cursor: pointer;
            margin-bottom: 15px;
        }
        
        .file-upload-icon {
            font-size: 40px;
            margin-bottom: 10px;
        }
        
        .file-info {
            background: #e8eaf6;
            padding: 15px;
            border-radius: 12px;
            margin-bottom: 15px;
            display: none;
            word-break: break-word;
        }
        
        .btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 15px 20px;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            width: 100%;
            cursor: pointer;
            margin-bottom: 10px;
            transition: transform 0.2s;
        }
        
        .btn:hover {
            transform: translateY(-2px);
        }
        
        .btn-small {
            padding: 8px 12px;
            font-size: 12px;
            width: auto;
            margin: 2px;
        }
        
        .btn-edit { background: #28a745; }
        .btn-delete { background: #dc3545; }
        .btn-copy { background: #17a2b8; }
        
        .snippet-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 15px;
            margin: 20px 0;
        }
        
        @media (min-width: 768px) {
            .snippet-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        
        .snippet-card {
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 15px;
        }
        
        .snippet-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            flex-wrap: wrap;
            gap: 10px;
        }
        
        .snippet-id {
            font-family: monospace;
            font-weight: bold;
            color: #667eea;
            font-size: 14px;
            background: #f0f2f5;
            padding: 5px 10px;
            border-radius: 20px;
        }
        
        .snippet-date {
            font-size: 12px;
            color: #999;
        }
        
        .snippet-preview {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            font-family: monospace;
            font-size: 13px;
            margin: 10px 0;
            max-height: 100px;
            overflow: hidden;
            white-space: pre-wrap;
            word-break: break-word;
        }
        
        .snippet-actions {
            display: flex;
            gap: 5px;
            flex-wrap: wrap;
        }
        
        .snippet-actions .btn-small {
            flex: 1;
            min-width: 60px;
        }
        
        .search-box {
            width: 100%;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            font-size: 16px;
            margin-bottom: 20px;
        }
        
        .result-box {
            background: linear-gradient(135deg, #667eea10 0%, #764ba210 100%);
            padding: 20px;
            border-radius: 12px;
            margin: 20px 0;
            display: none;
        }
        
        .url-box {
            background: white;
            padding: 15px;
            border-radius: 8px;
            word-break: break-all;
            font-family: monospace;
            margin: 10px 0;
            border: 1px solid #667eea;
        }
        
        .code-box {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 8px;
            font-family: monospace;
            overflow-x: auto;
            margin: 10px 0;
        }
        
        .footer {
            margin-top: 30px;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 12px;
            text-align: center;
        }
        
        .footer a {
            color: white;
            text-decoration: none;
            margin: 0 10px;
            display: inline-block;
            padding: 8px 15px;
            background: rgba(255,255,255,0.2);
            border-radius: 25px;
            font-size: 14px;
        }
        
        .footer-links {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 10px;
            margin: 15px 0;
        }
        
        .empty-state {
            text-align: center;
            padding: 40px 20px;
            color: #999;
        }
        
        .permanent-badge {
            background: #28a745;
            color: white;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 10px;
            margin-left: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 JSON Snippet Manager</h1>
        <p class="subtitle">Create • Share • Execute • Permanent JSON Storage</p>
        
        <div style="text-align: center; margin-bottom: 20px;">
            <span class="json-badge">💾 Saved in snippets.json</span>
        </div>
        
        <!-- Stats -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value" id="totalSnippets">0</div>
                <div class="stat-label">Total Snippets</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="todaySnippets">0</div>
                <div class="stat-label">Today</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="weekSnippets">0</div>
                <div class="stat-label">This Week</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="monthSnippets">0</div>
                <div class="stat-label">This Month</div>
            </div>
        </div>
        
        <!-- Tabs -->
        <div class="tabs">
            <div class="tab active" onclick="switchTab('create')">📝 Create</div>
            <div class="tab" onclick="switchTab('upload')">📁 Upload</div>
            <div class="tab" onclick="switchTab('view')">👁️ All</div>
            <div class="tab" onclick="switchTab('search')">🔍 Search</div>
        </div>
        
        <!-- Create Tab -->
        <div id="createTab" class="tab-content active">
            <textarea id="code" placeholder="# Write your Python code here
print('Hello World!')"></textarea>
            <button class="btn" onclick="createSnippet()">🔗 Generate Permanent Link</button>
        </div>
        
        <!-- Upload Tab -->
        <div id="uploadTab" class="tab-content">
            <div class="file-upload-area" onclick="document.getElementById('fileInput').click()">
                <div class="file-upload-icon">📂</div>
                <h3>Tap to upload file</h3>
                <p style="color: #666;">.py or .txt files</p>
                <input type="file" id="fileInput" accept=".py,.txt" style="display: none;" onchange="handleFileSelect(event)">
            </div>
            
            <div class="file-info" id="fileInfo">
                <strong>File:</strong> <span id="fileName"></span><br>
                <strong>Size:</strong> <span id="fileSize"></span>
            </div>
            
            <button class="btn" onclick="uploadFile()">📤 Upload & Save</button>
        </div>
        
        <!-- View All Tab -->
        <div id="viewTab" class="tab-content">
            <div id="allSnippets"></div>
            <button class="btn" onclick="loadAllSnippets()" style="background: #6c757d;">🔄 Refresh</button>
        </div>
        
        <!-- Search Tab -->
        <div id="searchTab" class="tab-content">
            <input type="text" class="search-box" id="searchInput" placeholder="Search by code or ID..." onkeyup="searchSnippets()">
            <div id="searchResults"></div>
        </div>
        
        <!-- Result Box -->
        <div id="result" class="result-box">
            <h3 style="margin-bottom: 15px;">✅ Saved to JSON!</h3>
            
            <p><strong>🔗 Your URL:</strong></p>
            <div class="url-box" id="snippetUrl"></div>
            
            <p><strong>🐍 Python Code:</strong></p>
            <div class="code-box" id="execCode"></div>
            
            <div style="display: flex; gap: 10px;">
                <button class="btn-small btn-copy" onclick="copyUrl()" style="flex: 1;">📋 Copy URL</button>
                <button class="btn-small btn-copy" onclick="copyCode()" style="flex: 1;">📋 Copy Code</button>
            </div>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <div class="footer-links">
                <a href="https://t.me/Aotpy" target="_blank">📱 @Aotpy</a>
                <a href="https://t.me/ObitoStuffs" target="_blank">📢 @ObitoStuffs</a>
                <a href="https://Aotpy.vercel.app" target="_blank">🌐 Portfolio</a>
            </div>
            <p style="font-size: 12px; opacity: 0.8; margin-top: 15px;">
                💾 Data permanently saved in <strong>snippets.json</strong> | Auto-create if not exists!
            </p>
        </div>
    </div>

    <script>
        const baseUrl = window.location.origin;
        let selectedFile = null;
        
        window.onload = function() {
            loadAllSnippets();
            updateStats();
        };
        
        function switchTab(tab) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            if (tab === 'create') {
                document.querySelectorAll('.tab')[0].classList.add('active');
                document.getElementById('createTab').classList.add('active');
            } else if (tab === 'upload') {
                document.querySelectorAll('.tab')[1].classList.add('active');
                document.getElementById('uploadTab').classList.add('active');
            } else if (tab === 'view') {
                document.querySelectorAll('.tab')[2].classList.add('active');
                document.getElementById('viewTab').classList.add('active');
                loadAllSnippets();
            } else if (tab === 'search') {
                document.querySelectorAll('.tab')[3].classList.add('active');
                document.getElementById('searchTab').classList.add('active');
            }
        }
        
        async function createSnippet() {
            const code = document.getElementById('code').value.trim();
            if (!code) {
                alert('Please enter some code!');
                return;
            }
            
            try {
                const response = await fetch('/api/snippets', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ code: code })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    showResult(data.id);
                    document.getElementById('code').value = '';
                    loadAllSnippets();
                    updateStats();
                    alert('✅ Saved to snippets.json permanently!');
                }
            } catch (error) {
                alert('Error: ' + error);
            }
        }
        
        function handleFileSelect(event) {
            const file = event.target.files[0];
            if (file) {
                selectedFile = file;
                document.getElementById('fileName').textContent = file.name;
                document.getElementById('fileSize').textContent = (file.size / 1024).toFixed(2) + ' KB';
                document.getElementById('fileInfo').style.display = 'block';
            }
        }
        
        async function uploadFile() {
            if (!selectedFile) {
                alert('Please select a file!');
                return;
            }
            
            const reader = new FileReader();
            reader.onload = async function(e) {
                const code = e.target.result;
                
                const response = await fetch('/api/snippets', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ code: code })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    showResult(data.id);
                    document.getElementById('fileInput').value = '';
                    document.getElementById('fileInfo').style.display = 'none';
                    selectedFile = null;
                    loadAllSnippets();
                    updateStats();
                    alert('✅ File saved to snippets.json!');
                }
            };
            reader.readAsText(selectedFile);
        }
        
        function showResult(id) {
            const url = `${baseUrl}/snippet/${id}`;
            const execCode = `import requests\\nexec(requests.get('${url}').text)`;
            
            document.getElementById('snippetUrl').textContent = url;
            document.getElementById('execCode').textContent = execCode;
            document.getElementById('result').style.display = 'block';
        }
        
        async function loadAllSnippets() {
            const container = document.getElementById('allSnippets');
            
            try {
                const response = await fetch('/api/all-snippets');
                const snippets = await response.json();
                
                if (snippets.length === 0) {
                    container.innerHTML = '<div class="empty-state"><div class="file-upload-icon">📝</div><p>No snippets yet. Create one!</p></div>';
                    return;
                }
                
                let html = '<div class="snippet-grid">';
                
                snippets.reverse().forEach(s => {
                    const date = new Date(s.created_at * 1000).toLocaleString();
                    const preview = s.preview || s.code.substring(0, 100) + '...';
                    
                    html += `
                        <div class="snippet-card">
                            <div class="snippet-header">
                                <span class="snippet-id">${s.id}</span>
                                <span class="snippet-date">${date}</span>
                            </div>
                            <div class="snippet-preview">${escapeHtml(preview)}</div>
                            <div class="snippet-actions">
                                <button class="btn-small" onclick="viewSnippet('${s.id}')">👁️ View</button>
                                <button class="btn-small btn-edit" onclick="editSnippet('${s.id}')">✏️ Edit</button>
                                <button class="btn-small btn-delete" onclick="deleteSnippet('${s.id}')">🗑️ Del</button>
                                <button class="btn-small btn-copy" onclick="copyUrl('${s.id}')">🔗 URL</button>
                            </div>
                        </div>
                    `;
                });
                
                html += '</div>';
                container.innerHTML = html;
            } catch (error) {
                container.innerHTML = '<div class="empty-state">Error loading snippets</div>';
            }
        }
        
        async function searchSnippets() {
            const query = document.getElementById('searchInput').value.toLowerCase();
            
            if (!query) {
                document.getElementById('searchResults').innerHTML = '';
                return;
            }
            
            const response = await fetch('/api/all-snippets');
            const snippets = await response.json();
            
            const filtered = snippets.filter(s => 
                s.code.toLowerCase().includes(query) || 
                s.id.toLowerCase().includes(query)
            );
            
            if (filtered.length === 0) {
                document.getElementById('searchResults').innerHTML = '<div class="empty-state">No matches</div>';
                return;
            }
            
            let html = '<div class="snippet-grid">';
            
            filtered.reverse().forEach(s => {
                const date = new Date(s.created_at * 1000).toLocaleString();
                const preview = s.preview || s.code.substring(0, 100) + '...';
                
                html += `
                    <div class="snippet-card">
                        <div class="snippet-header">
                            <span class="snippet-id">${s.id}</span>
                            <span class="snippet-date">${date}</span>
                        </div>
                        <div class="snippet-preview">${escapeHtml(preview)}</div>
                        <div class="snippet-actions">
                            <button class="btn-small" onclick="viewSnippet('${s.id}')">👁️ View</button>
                            <button class="btn-small btn-edit" onclick="editSnippet('${s.id}')">✏️ Edit</button>
                            <button class="btn-small btn-delete" onclick="deleteSnippet('${s.id}')">🗑️ Del</button>
                            <button class="btn-small btn-copy" onclick="copyUrl('${s.id}')">🔗 URL</button>
                        </div>
                    </div>
                `;
            });
            
            html += '</div>';
            document.getElementById('searchResults').innerHTML = html;
        }
        
        async function updateStats() {
            const response = await fetch('/api/all-snippets');
            const snippets = await response.json();
            
            document.getElementById('totalSnippets').textContent = snippets.length;
            
            const now = new Date();
            const today = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
            const weekAgo = now.getTime() - (7 * 24 * 60 * 60 * 1000);
            const monthAgo = now.getTime() - (30 * 24 * 60 * 60 * 1000);
            
            let todayCount = 0, weekCount = 0, monthCount = 0;
            
            snippets.forEach(s => {
                const date = s.created_at * 1000;
                if (date >= today) todayCount++;
                if (date >= weekAgo) weekCount++;
                if (date >= monthAgo) monthCount++;
            });
            
            document.getElementById('todaySnippets').textContent = todayCount;
            document.getElementById('weekSnippets').textContent = weekCount;
            document.getElementById('monthSnippets').textContent = monthCount;
        }
        
        function viewSnippet(id) {
            window.open(`/snippet/${id}`, '_blank');
        }
        
        async function editSnippet(id) {
            const newCode = prompt('Edit your code:');
            if (!newCode) return;
            
            const response = await fetch(`/api/snippets/${id}`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ code: newCode })
            });
            
            if (response.ok) {
                alert('✅ Updated in JSON!');
                loadAllSnippets();
                updateStats();
            }
        }
        
        async function deleteSnippet(id) {
            if (!confirm('Permanently delete from JSON?')) return;
            
            const response = await fetch(`/api/snippets/${id}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                alert('✅ Deleted from JSON!');
                loadAllSnippets();
                updateStats();
                if (document.getElementById('searchTab').classList.contains('active')) {
                    searchSnippets();
                }
            }
        }
        
        function copyUrl(id) {
            const url = `${baseUrl}/snippet/${id}`;
            navigator.clipboard.writeText(url);
            alert('✅ URL copied!');
        }
        
        function copyCode() {
            const text = document.getElementById('execCode').textContent;
            navigator.clipboard.writeText(text);
            alert('✅ Code copied!');
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    </script>
</body>
</html>
"""

# ========== API ROUTES ==========

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/api/snippets', methods=['POST'])
def create_snippet():
    global snippets
    data = request.json
    code = data.get('code', '').strip()
    
    if not code:
        return jsonify({'error': 'No code provided'}), 400
    
    snippet_id = str(uuid.uuid4())[:8]
    
    snippets[snippet_id] = {
        'id': snippet_id,
        'code': code,
        'created_at': datetime.now().timestamp(),
        'preview': code[:100] + '...' if len(code) > 100 else code
    }
    
    save_snippets(snippets)
    return jsonify({'id': snippet_id})

@app.route('/api/all-snippets', methods=['GET'])
def get_all_snippets():
    return jsonify(list(snippets.values()))

@app.route('/api/snippets/<snippet_id>', methods=['PUT'])
def update_snippet(snippet_id):
    global snippets
    if snippet_id not in snippets:
        return jsonify({'error': 'Not found'}), 404
    
    data = request.json
    new_code = data.get('code', '').strip()
    
    if not new_code:
        return jsonify({'error': 'No code provided'}), 400
    
    snippets[snippet_id]['code'] = new_code
    snippets[snippet_id]['preview'] = new_code[:100] + '...' if len(new_code) > 100 else new_code
    
    save_snippets(snippets)
    return jsonify({'success': True})

@app.route('/api/snippets/<snippet_id>', methods=['DELETE'])
def delete_snippet(snippet_id):
    global snippets
    if snippet_id in snippets:
        del snippets[snippet_id]
        save_snippets(snippets)
        return jsonify({'success': True})
    return jsonify({'error': 'Not found'}), 404

@app.route('/snippet/<snippet_id>')
def get_snippet(snippet_id):
    if snippet_id in snippets:
        return snippets[snippet_id]['code']
    return "Snippet not found", 404

if __name__ == '__main__':
    print("="*60)
    print("✅ JSON PERMANENT STORAGE SNIPPET MANAGER")
    print("="*60)
    print(f"📍 Open: http://localhost:5000")
    print(f"📁 Data file: {DATA_FILE}")
    print(f"📊 Total snippets loaded: {len(snippets)}")
    print("="*60)
    print("💾 Features:")
    print("   • ✅ Auto-create snippets.json if not exists")
    print("   • ✅ Server restart se bhi data safe!")
    print("   • ✅ Har action ke baad JSON update")
    print("   • ✅ Permanent storage - kabhi delete nahi")
    print("="*60)
    app.run(debug=True, port=5000)
