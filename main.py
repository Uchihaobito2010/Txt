from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
from flask_cors import CORS
import uuid
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.secret_key = 'aotpy-secret-key-2024'  # Change this in production
CORS(app)

# Store code snippets (permanent storage - kabhi delete nahi honge)
code_snippets = {}

# Single user credentials (simple - change karo apne hisaab se)
USERNAME = "admin"
PASSWORD = "admin123"  # Change this to your password

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return jsonify({'error': 'Please login first'}), 401
        return f(*args, **kwargs)
    return decorated_function

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
            max-width: 1000px;
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
            position: relative;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            opacity: 0.9;
            font-size: 1.1em;
        }
        
        .user-status {
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(255,255,255,0.2);
            padding: 8px 15px;
            border-radius: 50px;
            font-size: 0.9em;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .logout-btn {
            background: rgba(255,255,255,0.3);
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.8em;
        }
        
        .logout-btn:hover {
            background: rgba(255,255,255,0.4);
        }
        
        .login-container {
            max-width: 400px;
            margin: 50px auto;
            padding: 30px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .login-container h2 {
            color: #667eea;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .login-input {
            width: 100%;
            padding: 12px;
            margin-bottom: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1em;
        }
        
        .login-input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .login-btn {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1.1em;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .login-btn:hover {
            transform: translateY(-2px);
        }
        
        .error-msg {
            color: #dc3545;
            text-align: center;
            margin-top: 10px;
            display: none;
        }
        
        .main-content {
            padding: 30px;
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
            transition: all 0.3s;
        }
        
        .tab.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
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
        }
        
        textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .file-upload-area {
            border: 2px dashed #667eea;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            background: #f8f9fa;
            cursor: pointer;
        }
        
        .file-upload-area:hover {
            background: #e8eaf6;
        }
        
        .file-info {
            margin-top: 15px;
            padding: 10px;
            background: #e8eaf6;
            border-radius: 5px;
            display: none;
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
        
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            font-size: 1.1em;
            font-weight: 600;
            border-radius: 10px;
            cursor: pointer;
            transition: transform 0.2s;
            width: 100%;
            margin-bottom: 10px;
        }
        
        button:hover {
            transform: translateY(-2px);
        }
        
        button.secondary {
            background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
        }
        
        button.danger {
            background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
        }
        
        button.success {
            background: linear-gradient(135deg, #28a745 0%, #218838 100%);
        }
        
        .result-section {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-top: 30px;
        }
        
        .url-box {
            background: white;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            word-break: break-all;
            font-family: monospace;
        }
        
        .code-example {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 8px;
            font-family: monospace;
            overflow-x: auto;
        }
        
        .copy-btn {
            background: #28a745;
            margin-top: 10px;
            padding: 10px;
        }
        
        .snippet-list {
            max-height: 400px;
            overflow-y: auto;
        }
        
        .snippet-item {
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
        }
        
        .snippet-item-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .snippet-id {
            font-family: monospace;
            font-size: 1.2em;
            color: #667eea;
            font-weight: bold;
        }
        
        .snippet-type {
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
        }
        
        .type-permanent {
            background: #28a745;
            color: white;
        }
        
        .snippet-preview {
            color: #666;
            font-family: monospace;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        .snippet-actions {
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }
        
        .snippet-actions button {
            padding: 8px;
            font-size: 0.9em;
            width: auto;
        }
        
        .edit-section {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
            border-left: 4px solid #667eea;
        }
        
        .footer {
            background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .contact-links {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin: 25px 0;
            flex-wrap: wrap;
        }
        
        .contact-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 10px;
        }
        
        .contact-icon {
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
        }
        
        .contact-value {
            color: white;
            text-decoration: none;
        }
        
        .contact-value:hover {
            color: #667eea;
        }
        
        .portfolio-link {
            display: inline-block;
            margin-top: 20px;
            padding: 12px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 50px;
            font-weight: bold;
        }
        
        .disclaimer {
            margin-top: 20px;
            font-size: 0.8em;
            color: #a0aec0;
        }
        
        .search-box {
            width: 100%;
            padding: 10px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Python Code Snippet Manager</h1>
            <p>Store, Edit & Execute Python Code Remotely</p>
            
            <div class="user-status" id="userStatus" style="display: none;">
                <span id="username"></span>
                <button class="logout-btn" onclick="logout()">Logout</button>
            </div>
        </div>
        
        <!-- Login Page -->
        <div id="loginPage">
            <div class="login-container">
                <h2>🔐 Login</h2>
                <input type="text" id="username" class="login-input" placeholder="Username" value="admin">
                <input type="password" id="password" class="login-input" placeholder="Password" value="admin123">
                <button class="login-btn" onclick="login()">Login</button>
                <div id="loginError" class="error-msg">Invalid credentials!</div>
            </div>
        </div>
        
        <!-- Main App (Hidden until login) -->
        <div id="mainApp" style="display: none;">
            <div class="main-content">
                <div class="tabs">
                    <div class="tab active" onclick="switchTab('create')">📝 Create New</div>
                    <div class="tab" onclick="switchTab('manage')">🔧 Manage Snippets</div>
                    <div class="tab" onclick="switchTab('upload')">📁 Upload File</div>
                </div>
                
                <!-- Create New Tab -->
                <div id="create-tab" class="tab-content active">
                    <div class="input-section">
                        <div class="input-group">
                            <label>📝 Your Python Code:</label>
                            <textarea id="code" rows="10" placeholder="print('Hello, World!')"></textarea>
                        </div>
                        
                        <div class="options">
                            <div class="option-item">
                                <input type="radio" name="storage" id="permanent" value="permanent" checked>
                                <label for="permanent">💾 Permanent Storage</label>
                            </div>
                        </div>
                        
                        <button onclick="createSnippet()">🔗 Generate Link</button>
                    </div>
                </div>
                
                <!-- Upload File Tab -->
                <div id="upload-tab" class="tab-content">
                    <div class="input-section">
                        <div class="file-upload-area" onclick="document.getElementById('fileInput').click()">
                            <div style="font-size: 48px;">📁</div>
                            <h3>Click to upload file</h3>
                            <p>Upload .py or .txt files</p>
                            <input type="file" id="fileInput" accept=".py,.txt" style="display: none;" onchange="handleFileSelect(event)">
                        </div>
                        
                        <div class="file-info" id="fileInfo">
                            <strong>File:</strong> <span id="fileName"></span>
                            <br>
                            <strong>Size:</strong> <span id="fileSize"></span>
                        </div>
                        
                        <button onclick="uploadFile()" style="margin-top: 20px;">📤 Upload & Generate Link</button>
                    </div>
                </div>
                
                <!-- Manage Snippets Tab -->
                <div id="manage-tab" class="tab-content">
                    <div class="input-section">
                        <input type="text" class="search-box" placeholder="🔍 Search snippets..." onkeyup="searchSnippets(this.value)">
                        
                        <div class="snippet-list" id="snippetList">
                            <!-- Snippets will be loaded here -->
                        </div>
                        
                        <button class="secondary" onclick="loadSnippets()">🔄 Refresh List</button>
                    </div>
                </div>
                
                <!-- Edit Section -->
                <div id="editSection" class="edit-section" style="display: none;">
                    <h3>✏️ Edit Snippet: <span id="editId"></span></h3>
                    <div class="input-group">
                        <textarea id="editCode" rows="10"></textarea>
                    </div>
                    <button class="success" onclick="updateSnippet()">💾 Save Changes</button>
                    <button class="secondary" onclick="cancelEdit()">❌ Cancel</button>
                </div>
                
                <!-- Result Section -->
                <div class="result-section" id="result" style="display: none;">
                    <h3>✅ Your Code Link is Ready!</h3>
                    <div class="url-box" id="snippetUrl"></div>
                    
                    <h3>📋 Python Execution Code:</h3>
                    <div class="code-example" id="execCode"></div>
                    <button class="copy-btn" onclick="copyToClipboard()">📋 Copy to Clipboard</button>
                </div>
            </div>
            
            <!-- Footer -->
            <div class="footer">
                <div class="footer-content">
                    <h3>📬 Connect With Me</h3>
                    
                    <div class="contact-links">
                        <div class="contact-item">
                            <div class="contact-icon">📱</div>
                            <span>Telegram</span>
                            <a href="https://t.me/Aotpy" target="_blank" class="contact-value">@Aotpy</a>
                        </div>
                        
                        <div class="contact-item">
                            <div class="contact-icon">📢</div>
                            <span>Channel</span>
                            <a href="https://t.me/ObitoStuffs" target="_blank" class="contact-value">@ObitoStuffs</a>
                        </div>
                    </div>
                    
                    <a href="https://Aotpy.vercel.app" target="_blank" class="portfolio-link">
                        🌐 Visit My Portfolio
                    </a>
                    
                    <div class="disclaimer">
                        ⚠️ Disclaimer: Only execute code from trusted sources.
                        <br>
                        Made with ❤️ by Aotpy
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const baseUrl = window.location.origin;
        let currentEditId = null;
        let selectedFile = null;
        
        // Check login status on page load
        checkLoginStatus();
        
        async function checkLoginStatus() {
            try {
                const response = await fetch('/api/check-auth');
                const data = await response.json();
                
                if (data.logged_in) {
                    showMainApp(data.username);
                } else {
                    showLogin();
                }
            } catch (error) {
                showLogin();
            }
        }
        
        function showLogin() {
            document.getElementById('loginPage').style.display = 'block';
            document.getElementById('mainApp').style.display = 'none';
            document.getElementById('userStatus').style.display = 'none';
        }
        
        function showMainApp(username) {
            document.getElementById('loginPage').style.display = 'none';
            document.getElementById('mainApp').style.display = 'block';
            document.getElementById('userStatus').style.display = 'flex';
            document.getElementById('username').textContent = username;
        }
        
        async function login() {
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ username, password })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    showMainApp(username);
                } else {
                    document.getElementById('loginError').style.display = 'block';
                }
            } catch (error) {
                document.getElementById('loginError').style.display = 'block';
            }
        }
        
        async function logout() {
            await fetch('/api/logout', { method: 'POST' });
            showLogin();
        }
        
        // Tab switching
        function switchTab(tab) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            if (tab === 'create') {
                document.querySelectorAll('.tab')[0].classList.add('active');
                document.getElementById('create-tab').classList.add('active');
            } else if (tab === 'manage') {
                document.querySelectorAll('.tab')[1].classList.add('active');
                document.getElementById('manage-tab').classList.add('active');
                loadSnippets();
            } else if (tab === 'upload') {
                document.querySelectorAll('.tab')[2].classList.add('active');
                document.getElementById('upload-tab').classList.add('active');
            }
        }
        
        // File upload handling
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
                alert('Please select a file first!');
                return;
            }
            
            const reader = new FileReader();
            reader.onload = async function(e) {
                await createSnippetWithCode(e.target.result);
            };
            reader.readAsText(selectedFile);
        }
        
        async function createSnippet() {
            const code = document.getElementById('code').value.trim();
            if (!code) {
                alert('Please enter some code!');
                return;
            }
            
            await createSnippetWithCode(code);
        }
        
        async function createSnippetWithCode(code) {
            try {
                const response = await fetch('/api/snippets', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ code: code })
                });
                
                if (response.status === 401) {
                    alert('Please login first!');
                    showLogin();
                    return;
                }
                
                const data = await response.json();
                
                if (response.ok) {
                    const snippetUrl = `${baseUrl}/snippet/${data.id}`;
                    const execCode = `import requests\\nexec(requests.get('${snippetUrl}').text)`;
                    
                    document.getElementById('snippetUrl').textContent = snippetUrl;
                    document.getElementById('execCode').textContent = execCode;
                    document.getElementById('result').style.display = 'block';
                    
                    // Clear inputs
                    document.getElementById('code').value = '';
                    document.getElementById('fileInput').value = '';
                    document.getElementById('fileInfo').style.display = 'none';
                    selectedFile = null;
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (error) {
                alert('Error creating snippet: ' + error);
            }
        }
        
        async function loadSnippets() {
            try {
                const response = await fetch('/api/snippets/list');
                
                if (response.status === 401) {
                    showLogin();
                    return;
                }
                
                const snippets = await response.json();
                
                const snippetList = document.getElementById('snippetList');
                snippetList.innerHTML = '';
                
                if (snippets.length === 0) {
                    snippetList.innerHTML = '<p style="text-align: center;">No snippets found</p>';
                    return;
                }
                
                snippets.forEach(snippet => {
                    const div = document.createElement('div');
                    div.className = 'snippet-item';
                    div.innerHTML = `
                        <div class="snippet-item-header">
                            <span class="snippet-id">${snippet.id}</span>
                            <span class="snippet-type type-permanent">Permanent</span>
                        </div>
                        <div class="snippet-preview">${snippet.preview}</div>
                        <div class="snippet-actions">
                            <button class="success" onclick="editSnippet('${snippet.id}')">✏️ Edit</button>
                            <button class="danger" onclick="deleteSnippet('${snippet.id}')">🗑️ Delete</button>
                            <button onclick="viewSnippet('${snippet.id}')">👁️ View</button>
                            <button onclick="copySnippetUrl('${snippet.id}')">🔗 Copy URL</button>
                        </div>
                        <small>Created: ${new Date(snippet.created_at * 1000).toLocaleString()}</small>
                    `;
                    snippetList.appendChild(div);
                });
            } catch (error) {
                alert('Error loading snippets: ' + error);
            }
        }
        
        function searchSnippets(query) {
            const items = document.querySelectorAll('.snippet-item');
            items.forEach(item => {
                const text = item.textContent.toLowerCase();
                item.style.display = text.includes(query.toLowerCase()) ? 'block' : 'none';
            });
        }
        
        async function editSnippet(id) {
            try {
                const response = await fetch(`/snippet/${id}`);
                const code = await response.text();
                
                currentEditId = id;
                document.getElementById('editId').textContent = id;
                document.getElementById('editCode').value = code;
                document.getElementById('editSection').style.display = 'block';
            } catch (error) {
                alert('Error loading snippet: ' + error);
            }
        }
        
        async function updateSnippet() {
            if (!currentEditId) return;
            
            const code = document.getElementById('editCode').value.trim();
            if (!code) {
                alert('Code cannot be empty!');
                return;
            }
            
            try {
                const response = await fetch(`/api/snippets/${currentEditId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ code: code })
                });
                
                if (response.ok) {
                    alert('✅ Snippet updated!');
                    cancelEdit();
                    loadSnippets();
                } else {
                    alert('Error updating snippet');
                }
            } catch (error) {
                alert('Error: ' + error);
            }
        }
        
        async function deleteSnippet(id) {
            if (!confirm('Delete this snippet?')) return;
            
            try {
                const response = await fetch(`/api/snippets/${id}`, {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    alert('✅ Snippet deleted!');
                    loadSnippets();
                }
            } catch (error) {
                alert('Error: ' + error);
            }
        }
        
        function viewSnippet(id) {
            window.open(`/snippet/${id}`, '_blank');
        }
        
        function copySnippetUrl(id) {
            const url = `${baseUrl}/snippet/${id}`;
            navigator.clipboard.writeText(url);
            alert('✅ URL copied!');
        }
        
        function cancelEdit() {
            currentEditId = null;
            document.getElementById('editSection').style.display = 'none';
        }
        
        async function copyToClipboard() {
            const text = document.getElementById('execCode').textContent;
            await navigator.clipboard.writeText(text);
            alert('✅ Copied!');
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

# ========== LOGIN ROUTES ==========

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if username == USERNAME and password == PASSWORD:
        session['logged_in'] = True
        session['username'] = username
        return jsonify({'success': True, 'username': username})
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    if 'logged_in' in session:
        return jsonify({'logged_in': True, 'username': session.get('username')})
    return jsonify({'logged_in': False})

# ========== SNIPPET ROUTES (Protected) ==========

@app.route('/api/snippets', methods=['POST'])
@login_required
def create_snippet():
    data = request.json
    code = data.get('code')
    
    if not code:
        return jsonify({'error': 'No code provided'}), 400
    
    # Generate unique ID
    snippet_id = str(uuid.uuid4())[:8]
    
    # Store the snippet (permanent - kabhi nahi hatega)
    code_snippets[snippet_id] = {
        'code': code,
        'created_at': datetime.now().timestamp(),
        'storage_type': 'permanent',
        'preview': code[:100] + '...' if len(code) > 100 else code
    }
    
    return jsonify({
        'id': snippet_id,
        'storage_type': 'permanent'
    })

@app.route('/api/snippets/<snippet_id>', methods=['PUT'])
@login_required
def update_snippet(snippet_id):
    if snippet_id not in code_snippets:
        return jsonify({'error': 'Snippet not found'}), 404
    
    data = request.json
    new_code = data.get('code')
    
    if not new_code:
        return jsonify({'error': 'No code provided'}), 400
    
    # Update the snippet
    code_snippets[snippet_id]['code'] = new_code
    code_snippets[snippet_id]['preview'] = new_code[:100] + '...' if len(new_code) > 100 else new_code
    code_snippets[snippet_id]['updated_at'] = datetime.now().timestamp()
    
    return jsonify({'message': 'Snippet updated successfully'})

@app.route('/api/snippets/<snippet_id>', methods=['DELETE'])
@login_required
def delete_snippet(snippet_id):
    if snippet_id in code_snippets:
        del code_snippets[snippet_id]
        return jsonify({'message': 'Snippet deleted'})
    return jsonify({'error': 'Snippet not found'}), 404

@app.route('/api/snippets/list', methods=['GET'])
@login_required
def list_snippets():
    # Return all snippets (permanent - kabhi delete nahi honge)
    snippets_list = []
    for snippet_id, snippet in code_snippets.items():
        snippets_list.append({
            'id': snippet_id,
            'created_at': snippet['created_at'],
            'storage_type': 'permanent',
            'preview': snippet['preview']
        })
    
    return jsonify(snippets_list)

# ========== PUBLIC ROUTE (No login required for viewing) ==========

@app.route('/snippet/<snippet_id>')
def get_snippet(snippet_id):
    snippet = code_snippets.get(snippet_id)
    
    if not snippet:
        return "Snippet not found", 404
    
    # Return the code as plain text (public - koi bhi dekh sakta hai)
    return snippet['code'], 200, {'Content-Type': 'text/plain'}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
