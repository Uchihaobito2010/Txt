from flask import Flask, request, jsonify, render_template_string, session
from flask_cors import CORS
import uuid
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'aotpy-secret-key-2024'  # Change this in production
CORS(app)

# Store users and their snippets
users_db = {}  # username: {password: hash, snippets: {}}
snippets_db = {}  # Global snippets storage with user_id

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return jsonify({'error': 'Please login first'}), 401
        return f(*args, **kwargs)
    return decorated_function

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Public Python Code Snippet Manager</title>
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
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .username {
            font-weight: bold;
        }
        
        .logout-btn {
            background: rgba(255,255,255,0.3);
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 5px;
            cursor: pointer;
        }
        
        .auth-container {
            max-width: 400px;
            margin: 50px auto;
            padding: 30px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .auth-tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 10px;
        }
        
        .auth-tab {
            flex: 1;
            text-align: center;
            padding: 10px;
            cursor: pointer;
            font-weight: 600;
            color: #666;
        }
        
        .auth-tab.active {
            color: #667eea;
            border-bottom: 3px solid #667eea;
        }
        
        .auth-form {
            display: none;
        }
        
        .auth-form.active {
            display: block;
        }
        
        .auth-input {
            width: 100%;
            padding: 12px;
            margin-bottom: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1em;
        }
        
        .auth-input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .auth-btn {
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
        
        .auth-btn:hover {
            transform: translateY(-2px);
        }
        
        .error-msg {
            color: #dc3545;
            text-align: center;
            margin-top: 10px;
            display: none;
        }
        
        .success-msg {
            color: #28a745;
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
        
        .snippet-owner {
            font-size: 0.8em;
            color: #666;
            background: #f0f0f0;
            padding: 3px 8px;
            border-radius: 4px;
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
        
        .stats-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        
        .stat-item {
            text-align: center;
        }
        
        .stat-value {
            font-size: 1.5em;
            font-weight: bold;
            color: #667eea;
        }
        
        .stat-label {
            color: #666;
            font-size: 0.9em;
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
            <h1>🚀 Public Python Code Snippet Manager</h1>
            <p>Create, Share & Execute Python Code - Free for Everyone!</p>
            
            <div class="user-status" id="userStatus" style="display: none;">
                <span class="username" id="username"></span>
                <button class="logout-btn" onclick="logout()">Logout</button>
            </div>
        </div>
        
        <!-- Auth Page -->
        <div id="authPage">
            <div class="auth-container">
                <div class="auth-tabs">
                    <div class="auth-tab active" onclick="switchAuthTab('login')">Login</div>
                    <div class="auth-tab" onclick="switchAuthTab('signup')">Sign Up</div>
                </div>
                
                <!-- Login Form -->
                <div id="loginForm" class="auth-form active">
                    <h2 style="text-align: center; margin-bottom: 20px;">🔐 Welcome Back!</h2>
                    <input type="text" id="loginUsername" class="auth-input" placeholder="Username">
                    <input type="password" id="loginPassword" class="auth-input" placeholder="Password">
                    <button class="auth-btn" onclick="login()">Login</button>
                    <div id="loginError" class="error-msg">Invalid credentials!</div>
                </div>
                
                <!-- Signup Form -->
                <div id="signupForm" class="auth-form">
                    <h2 style="text-align: center; margin-bottom: 20px;">📝 Create Account</h2>
                    <input type="text" id="signupUsername" class="auth-input" placeholder="Choose Username">
                    <input type="password" id="signupPassword" class="auth-input" placeholder="Choose Password">
                    <input type="password" id="signupConfirmPassword" class="auth-input" placeholder="Confirm Password">
                    <button class="auth-btn" onclick="signup()">Sign Up</button>
                    <div id="signupError" class="error-msg"></div>
                    <div id="signupSuccess" class="success-msg">Account created! Please login.</div>
                </div>
            </div>
        </div>
        
        <!-- Main App (Hidden until login) -->
        <div id="mainApp" style="display: none;">
            <div class="main-content">
                <!-- Stats Bar -->
                <div class="stats-bar">
                    <div class="stat-item">
                        <div class="stat-value" id="userSnippetCount">0</div>
                        <div class="stat-label">Your Snippets</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" id="totalSnippetCount">0</div>
                        <div class="stat-label">Total Snippets</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" id="userCount">0</div>
                        <div class="stat-label">Total Users</div>
                    </div>
                </div>
                
                <div class="tabs">
                    <div class="tab active" onclick="switchTab('create')">📝 Create New</div>
                    <div class="tab" onclick="switchTab('manage')">🔧 My Snippets</div>
                    <div class="tab" onclick="switchTab('upload')">📁 Upload File</div>
                    <div class="tab" onclick="switchTab('public')">🌍 Public Snippets</div>
                </div>
                
                <!-- Create New Tab -->
                <div id="create-tab" class="tab-content active">
                    <div class="input-section">
                        <div class="input-group">
                            <label>📝 Your Python Code:</label>
                            <textarea id="code" rows="10" placeholder="print('Hello, World!')"></textarea>
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
                
                <!-- My Snippets Tab -->
                <div id="manage-tab" class="tab-content">
                    <div class="input-section">
                        <input type="text" class="search-box" placeholder="🔍 Search my snippets..." onkeyup="searchMySnippets(this.value)">
                        
                        <div class="snippet-list" id="mySnippetList">
                            <!-- My snippets will be loaded here -->
                        </div>
                        
                        <button class="secondary" onclick="loadMySnippets()">🔄 Refresh</button>
                    </div>
                </div>
                
                <!-- Public Snippets Tab -->
                <div id="public-tab" class="tab-content">
                    <div class="input-section">
                        <input type="text" class="search-box" placeholder="🔍 Search all public snippets..." onkeyup="searchPublicSnippets(this.value)">
                        
                        <div class="snippet-list" id="publicSnippetList">
                            <!-- Public snippets will be loaded here -->
                        </div>
                        
                        <button class="secondary" onclick="loadPublicSnippets()">🔄 Refresh</button>
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
                        Made with ❤️ by Aotpy | Public Tool - Free for Everyone
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
                    loadStats();
                } else {
                    showAuth();
                }
            } catch (error) {
                showAuth();
            }
        }
        
        function showAuth() {
            document.getElementById('authPage').style.display = 'block';
            document.getElementById('mainApp').style.display = 'none';
            document.getElementById('userStatus').style.display = 'none';
        }
        
        function showMainApp(username) {
            document.getElementById('authPage').style.display = 'none';
            document.getElementById('mainApp').style.display = 'block';
            document.getElementById('userStatus').style.display = 'flex';
            document.getElementById('username').textContent = username;
        }
        
        function switchAuthTab(tab) {
            document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));
            
            if (tab === 'login') {
                document.querySelectorAll('.auth-tab')[0].classList.add('active');
                document.getElementById('loginForm').classList.add('active');
            } else {
                document.querySelectorAll('.auth-tab')[1].classList.add('active');
                document.getElementById('signupForm').classList.add('active');
            }
        }
        
        async function signup() {
            const username = document.getElementById('signupUsername').value.trim();
            const password = document.getElementById('signupPassword').value;
            const confirm = document.getElementById('signupConfirmPassword').value;
            
            if (!username || !password) {
                showError('signupError', 'Please fill all fields');
                return;
            }
            
            if (password !== confirm) {
                showError('signupError', 'Passwords do not match');
                return;
            }
            
            try {
                const response = await fetch('/api/signup', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ username, password })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    document.getElementById('signupSuccess').style.display = 'block';
                    document.getElementById('signupError').style.display = 'none';
                    
                    // Clear form
                    document.getElementById('signupUsername').value = '';
                    document.getElementById('signupPassword').value = '';
                    document.getElementById('signupConfirmPassword').value = '';
                    
                    // Switch to login tab after 2 seconds
                    setTimeout(() => {
                        switchAuthTab('login');
                        document.getElementById('signupSuccess').style.display = 'none';
                    }, 2000);
                } else {
                    showError('signupError', data.error);
                }
            } catch (error) {
                showError('signupError', 'Error creating account');
            }
        }
        
        async function login() {
            const username = document.getElementById('loginUsername').value;
            const password = document.getElementById('loginPassword').value;
            
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
                    loadStats();
                } else {
                    document.getElementById('loginError').style.display = 'block';
                }
            } catch (error) {
                document.getElementById('loginError').style.display = 'block';
            }
        }
        
        async function logout() {
            await fetch('/api/logout', { method: 'POST' });
            showAuth();
        }
        
        function showError(elementId, message) {
            const errorDiv = document.getElementById(elementId);
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
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
                loadMySnippets();
            } else if (tab === 'upload') {
                document.querySelectorAll('.tab')[2].classList.add('active');
                document.getElementById('upload-tab').classList.add('active');
            } else if (tab === 'public') {
                document.querySelectorAll('.tab')[3].classList.add('active');
                document.getElementById('public-tab').classList.add('active');
                loadPublicSnippets();
            }
        }
        
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const stats = await response.json();
                
                document.getElementById('userSnippetCount').textContent = stats.user_snippets;
                document.getElementById('totalSnippetCount').textContent = stats.total_snippets;
                document.getElementById('userCount').textContent = stats.total_users;
            } catch (error) {
                console.error('Error loading stats:', error);
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
                    alert('Session expired! Please login again.');
                    showAuth();
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
                    
                    // Refresh stats
                    loadStats();
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (error) {
                alert('Error creating snippet: ' + error);
            }
        }
        
        async function loadMySnippets() {
            try {
                const response = await fetch('/api/my-snippets');
                
                if (response.status === 401) {
                    showAuth();
                    return;
                }
                
                const snippets = await response.json();
                
                const snippetList = document.getElementById('mySnippetList');
                snippetList.innerHTML = '';
                
                if (snippets.length === 0) {
                    snippetList.innerHTML = '<p style="text-align: center;">You haven\'t created any snippets yet</p>';
                    return;
                }
                
                snippets.forEach(snippet => {
                    const div = createSnippetElement(snippet, true);
                    snippetList.appendChild(div);
                });
            } catch (error) {
                alert('Error loading snippets: ' + error);
            }
        }
        
        async function loadPublicSnippets() {
            try {
                const response = await fetch('/api/public-snippets');
                const snippets = await response.json();
                
                const snippetList = document.getElementById('publicSnippetList');
                snippetList.innerHTML = '';
                
                if (snippets.length === 0) {
                    snippetList.innerHTML = '<p style="text-align: center;">No public snippets yet</p>';
                    return;
                }
                
                snippets.forEach(snippet => {
                    const div = createSnippetElement(snippet, false);
                    snippetList.appendChild(div);
                });
            } catch (error) {
                alert('Error loading snippets: ' + error);
            }
        }
        
        function createSnippetElement(snippet, isOwner) {
            const div = document.createElement('div');
            div.className = 'snippet-item';
            
            let actions = '';
            if (isOwner) {
                actions = `
                    <div class="snippet-actions">
                        <button class="success" onclick="editSnippet('${snippet.id}')">✏️ Edit</button>
                        <button class="danger" onclick="deleteSnippet('${snippet.id}')">🗑️ Delete</button>
                        <button onclick="viewSnippet('${snippet.id}')">👁️ View</button>
                        <button onclick="copySnippetUrl('${snippet.id}')">🔗 Copy URL</button>
                    </div>
                `;
            } else {
                actions = `
                    <div class="snippet-actions">
                        <button onclick="viewSnippet('${snippet.id}')">👁️ View</button>
                        <button onclick="copySnippetUrl('${snippet.id}')">🔗 Copy URL</button>
                    </div>
                `;
            }
            
            div.innerHTML = `
                <div class="snippet-item-header">
                    <span class="snippet-id">${snippet.id}</span>
                    <span class="snippet-owner">by @${snippet.owner}</span>
                </div>
                <div class="snippet-preview">${snippet.preview}</div>
                ${actions}
                <small>Created: ${new Date(snippet.created_at * 1000).toLocaleString()}</small>
            `;
            
            return div;
        }
        
        function searchMySnippets(query) {
            searchSnippets('mySnippetList', query);
        }
        
        function searchPublicSnippets(query) {
            searchSnippets('publicSnippetList', query);
        }
        
        function searchSnippets(listId, query) {
            const items = document.querySelectorAll(`#${listId} .snippet-item`);
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
                    loadMySnippets();
                    loadPublicSnippets();
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
                    loadMySnippets();
                    loadPublicSnippets();
                    loadStats();
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

# ========== AUTH ROUTES ==========

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    if username in users_db:
        return jsonify({'error': 'Username already exists'}), 400
    
    # Create new user
    users_db[username] = {
        'password': password,  # In production, use password hashing
        'created_at': datetime.now().timestamp(),
        'snippets': {}
    }
    
    return jsonify({'success': True, 'message': 'Account created'})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if username in users_db and users_db[username]['password'] == password:
        session['user'] = username
        return jsonify({'success': True, 'username': username})
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    if 'user' in session:
        return jsonify({'logged_in': True, 'username': session['user']})
    return jsonify({'logged_in': False})

# ========== STATS ROUTES ==========

@app.route('/api/stats', methods=['GET'])
@login_required
def get_stats():
    current_user = session['user']
    
    # Count user's snippets
    user_snippets = len(users_db[current_user]['snippets'])
    
    # Count total snippets
    total_snippets = 0
    for user in users_db.values():
        total_snippets += len(user['snippets'])
    
    return jsonify({
        'user_snippets': user_snippets,
        'total_snippets': total_snippets,
        'total_users': len(users_db)
    })

# ========== SNIPPET ROUTES ==========

@app.route('/api/snippets', methods=['POST'])
@login_required
def create_snippet():
    current_user = session['user']
    data = request.json
    code = data.get('code')
    
    if not code:
        return jsonify({'error': 'No code provided'}), 400
    
    # Generate unique ID
    snippet_id = str(uuid.uuid4())[:8]
    
    # Store snippet with owner info
    snippet_data = {
        'id': snippet_id,
        'code': code,
        'owner': current_user,
        'created_at': datetime.now().timestamp(),
        'preview': code[:100] + '...' if len(code) > 100 else code
    }
    
    # Store in user's snippets
    users_db[current_user]['snippets'][snippet_id] = snippet_data
    
    return jsonify({
        'id': snippet_id,
        'owner': current_user
    })

@app.route('/api/my-snippets', methods=['GET'])
@login_required
def get_my_snippets():
    current_user = session['user']
    snippets = list(users_db[current_user]['snippets'].values())
    return jsonify(snippets)

@app.route('/api/public-snippets', methods=['GET'])
def get_public_snippets():
    all_snippets = []
    for user, user_data in users_db.items():
        for snippet in user_data['snippets'].values():
            all_snippets.append(snippet)
    
    # Sort by newest first
    all_snippets.sort(key=lambda x: x['created_at'], reverse=True)
    return jsonify(all_snippets)

@app.route('/api/snippets/<snippet_id>', methods=['PUT'])
@login_required
def update_snippet(snippet_id):
    current_user = session['user']
    
    # Check if snippet exists and belongs to user
    if snippet_id not in users_db[current_user]['snippets']:
        return jsonify({'error': 'Snippet not found or unauthorized'}), 404
    
    data = request.json
    new_code = data.get('code')
    
    if not new_code:
        return jsonify({'error': 'No code provided'}), 400
    
    # Update snippet
    users_db[current_user]['snippets'][snippet_id]['code'] = new_code
    users_db[current_user]['snippets'][snippet_id]['preview'] = new_code[:100] + '...' if len(new_code) > 100 else new_code
    users_db[current_user]['snippets'][snippet_id]['updated_at'] = datetime.now().timestamp()
    
    return jsonify({'message': 'Snippet updated'})

@app.route('/api/snippets/<snippet_id>', methods=['DELETE'])
@login_required
def delete_snippet(snippet_id):
    current_user = session['user']
    
    # Check if snippet exists and belongs to user
    if snippet_id not in users_db[current_user]['snippets']:
        return jsonify({'error': 'Snippet not found or unauthorized'}), 404
    
    # Delete snippet
    del users_db[current_user]['snippets'][snippet_id]
    
    return jsonify({'message': 'Snippet deleted'})

# ========== PUBLIC ROUTE (No login required) ==========

@app.route('/snippet/<snippet_id>')
def get_snippet(snippet_id):
    # Search for snippet in all users
    for user, user_data in users_db.items():
        if snippet_id in user_data['snippets']:
            return user_data['snippets'][snippet_id]['code'], 200, {'Content-Type': 'text/plain'}
    
    return "Snippet not found", 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
