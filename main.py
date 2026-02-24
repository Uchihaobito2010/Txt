from flask import Flask, request, jsonify, render_template_string, send_file
from flask_cors import CORS
import uuid
import os
from datetime import datetime, timedelta
import io

app = Flask(__name__)
CORS(app)

# Store code snippets
code_snippets = {}

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
            transition: border-color 0.3s;
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
            transition: all 0.3s;
        }
        
        .file-upload-area:hover {
            background: #e8eaf6;
            border-color: #764ba2;
        }
        
        .file-upload-area i {
            font-size: 48px;
            color: #667eea;
            margin-bottom: 10px;
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
            margin-bottom: 10px;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
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
        
        .edit-section {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
            border-left: 4px solid #667eea;
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
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .snippet-item:hover {
            border-color: #667eea;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
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
        
        .type-temporary {
            background: #ffc107;
            color: black;
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
            margin: 0;
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
        
        .search-box {
            width: 100%;
            padding: 10px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 1em;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Python Code Snippet Manager</h1>
            <p>Store, Edit & Execute Python Code Remotely</p>
        </div>
        
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
            </div>
            
            <!-- Upload File Tab -->
            <div id="upload-tab" class="tab-content">
                <div class="input-section">
                    <div class="file-upload-area" onclick="document.getElementById('fileInput').click()">
                        <div>📁</div>
                        <h3>Click to upload or drag and drop</h3>
                        <p>Upload .py files or text files</p>
                        <input type="file" id="fileInput" accept=".py,.txt" style="display: none;" onchange="handleFileSelect(event)">
                    </div>
                    
                    <div class="file-info" id="fileInfo">
                        <strong>Selected file:</strong> <span id="fileName"></span>
                        <br>
                        <strong>Size:</strong> <span id="fileSize"></span>
                    </div>
                    
                    <div class="options" style="margin-top: 20px;">
                        <div class="option-item">
                            <input type="radio" name="uploadStorage" id="uploadPermanent" value="permanent" checked>
                            <label for="uploadPermanent">💾 Permanent Storage</label>
                        </div>
                        <div class="option-item">
                            <input type="radio" name="uploadStorage" id="uploadTemporary" value="temporary">
                            <label for="uploadTemporary">⏱️ Temporary Storage</label>
                        </div>
                        <div class="option-item" id="uploadExpiryOption" style="display: none;">
                            <label for="uploadExpiry">Expires in (minutes):</label>
                            <input type="number" id="uploadExpiry" min="1" max="1440" value="60">
                        </div>
                    </div>
                    
                    <button onclick="uploadFile()">📤 Upload & Generate Link</button>
                </div>
            </div>
            
            <!-- Manage Snippets Tab -->
            <div id="manage-tab" class="tab-content">
                <div class="input-section">
                    <input type="text" class="search-box" placeholder="🔍 Search snippets..." onkeyup="searchSnippets(this.value)">
                    
                    <div class="snippet-list" id="snippetList">
                        <!-- Snippets will be loaded here -->
                    </div>
                    
                    <button class="secondary" onclick="loadSnippets()" style="margin-top: 20px;">🔄 Refresh List</button>
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
                
                <div id="statusMessage"></div>
            </div>
        </div>
        
        <div class="footer">
            <p>⚡ Use with caution: Only execute code from trusted sources!</p>
        </div>
    </div>

    <script>
        const baseUrl = window.location.origin;
        let currentEditId = null;
        let selectedFile = null;
        
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
        
        // Storage type options
        document.querySelectorAll('input[name="storage"]').forEach(radio => {
            radio.addEventListener('change', function() {
                document.getElementById('expiryOption').style.display = 
                    this.value === 'temporary' ? 'flex' : 'none';
            });
        });
        
        document.querySelectorAll('input[name="uploadStorage"]').forEach(radio => {
            radio.addEventListener('change', function() {
                document.getElementById('uploadExpiryOption').style.display = 
                    this.value === 'temporary' ? 'flex' : 'none';
            });
        });
        
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
        
        // Upload file
        async function uploadFile() {
            if (!selectedFile) {
                alert('Please select a file first!');
                return;
            }
            
            const reader = new FileReader();
            reader.onload = async function(e) {
                const code = e.target.result;
                const storageType = document.querySelector('input[name="uploadStorage"]:checked').value;
                const expiry = storageType === 'temporary' ? 
                    parseInt(document.getElementById('uploadExpiry').value) : null;
                
                await createSnippetWithCode(code, storageType, expiry);
            };
            reader.readAsText(selectedFile);
        }
        
        // Create snippet from text
        async function createSnippet() {
            const code = document.getElementById('code').value.trim();
            if (!code) {
                alert('Please enter some code!');
                return;
            }
            
            const storageType = document.querySelector('input[name="storage"]:checked').value;
            const expiry = storageType === 'temporary' ? 
                parseInt(document.getElementById('expiry').value) : null;
            
            await createSnippetWithCode(code, storageType, expiry);
        }
        
        // Create snippet API call
        async function createSnippetWithCode(code, storageType, expiry) {
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
        
        // Load all snippets
        async function loadSnippets() {
            try {
                const response = await fetch('/api/snippets/list');
                const snippets = await response.json();
                
                const snippetList = document.getElementById('snippetList');
                snippetList.innerHTML = '';
                
                if (snippets.length === 0) {
                    snippetList.innerHTML = '<p style="text-align: center; color: #666;">No snippets found</p>';
                    return;
                }
                
                snippets.forEach(snippet => {
                    const snippetElement = createSnippetElement(snippet);
                    snippetList.appendChild(snippetElement);
                });
            } catch (error) {
                alert('Error loading snippets: ' + error);
            }
        }
        
        // Create snippet element
        function createSnippetElement(snippet) {
            const div = document.createElement('div');
            div.className = 'snippet-item';
            
            const expiryText = snippet.expires_at ? 
                new Date(snippet.expires_at * 1000).toLocaleString() : 'Never';
            
            div.innerHTML = `
                <div class="snippet-item-header">
                    <span class="snippet-id">${snippet.id}</span>
                    <span class="snippet-type ${snippet.storage_type === 'permanent' ? 'type-permanent' : 'type-temporary'}">
                        ${snippet.storage_type}
                    </span>
                </div>
                <div class="snippet-preview">${snippet.preview}</div>
                <div class="snippet-actions">
                    <button class="success" onclick="editSnippet('${snippet.id}')">✏️ Edit</button>
                    <button class="danger" onclick="deleteSnippet('${snippet.id}')">🗑️ Delete</button>
                    <button onclick="viewSnippet('${snippet.id}')">👁️ View</button>
                    <button onclick="copySnippetUrl('${snippet.id}')">🔗 Copy URL</button>
                </div>
                <small>Created: ${new Date(snippet.created_at * 1000).toLocaleString()}</small>
                <br>
                <small>Expires: ${expiryText}</small>
            `;
            
            return div;
        }
        
        // Search snippets
        function searchSnippets(query) {
            const items = document.querySelectorAll('.snippet-item');
            items.forEach(item => {
                const text = item.textContent.toLowerCase();
                if (text.includes(query.toLowerCase())) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        }
        
        // Edit snippet
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
        
        // Update snippet
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
                    alert('✅ Snippet updated successfully!');
                    cancelEdit();
                    loadSnippets();
                } else {
                    alert('Error updating snippet');
                }
            } catch (error) {
                alert('Error: ' + error);
            }
        }
        
        // Delete snippet
        async function deleteSnippet(id) {
            if (!confirm('Are you sure you want to delete this snippet?')) return;
            
            try {
                const response = await fetch(`/api/snippets/${id}`, {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    alert('✅ Snippet deleted successfully!');
                    loadSnippets();
                } else {
                    alert('Error deleting snippet');
                }
            } catch (error) {
                alert('Error: ' + error);
            }
        }
        
        // View snippet
        function viewSnippet(id) {
            window.open(`/snippet/${id}`, '_blank');
        }
        
        // Copy snippet URL
        function copySnippetUrl(id) {
            const url = `${baseUrl}/snippet/${id}`;
            navigator.clipboard.writeText(url);
            alert('✅ URL copied to clipboard!');
        }
        
        // Cancel edit
        function cancelEdit() {
            currentEditId = null;
            document.getElementById('editSection').style.display = 'none';
            document.getElementById('editCode').value = '';
        }
        
        // Copy to clipboard
        async function copyToClipboard() {
            const execCode = document.getElementById('execCode').textContent;
            try {
                await navigator.clipboard.writeText(execCode);
                alert('✅ Copied to clipboard!');
            } catch (err) {
                alert('❌ Failed to copy');
            }
        }
        
        // Load snippets when switching to manage tab
        setInterval(() => {
            if (document.getElementById('manage-tab').classList.contains('active')) {
                loadSnippets();
            }
        }, 30000); // Refresh every 30 seconds
    </script>
</body>
</html>
<div class="credit">
<p>👨‍💻 Developer :
<span class="tg" onclick="window.open('https://t.me/Aotpy','_blank')">@Aotpy</span></p>

<p>🌐 Portfolio :
<span class="tg" onclick="window.open('https://aotpy.vercel.app','_blank')">Portfolio</span></p>

<p>📢 Channel :
<span class="tg" onclick="window.open('https://t.me/obitostuffs','_blank')">@obitostuffs</span></p>

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
        'storage_type': storage_type,
        'preview': code[:100] + '...' if len(code) > 100 else code
    }
    
    return jsonify({
        'id': snippet_id,
        'expires_at': expires_at,
        'storage_type': storage_type
    })

@app.route('/api/snippets/<snippet_id>', methods=['PUT'])
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
def delete_snippet(snippet_id):
    if snippet_id in code_snippets:
        del code_snippets[snippet_id]
        return jsonify({'message': 'Snippet deleted'})
    return jsonify({'error': 'Snippet not found'}), 404

@app.route('/api/snippets/list', methods=['GET'])
def list_snippets():
    # Clean up expired snippets first
    current_time = datetime.now().timestamp()
    expired = []
    
    for snippet_id, snippet in list(code_snippets.items()):
        if snippet.get('expires_at') and current_time > snippet['expires_at']:
            expired.append(snippet_id)
            del code_snippets[snippet_id]
    
    # Return all active snippets
    snippets_list = []
    for snippet_id, snippet in code_snippets.items():
        snippets_list.append({
            'id': snippet_id,
            'created_at': snippet['created_at'],
            'expires_at': snippet['expires_at'],
            'storage_type': snippet['storage_type'],
            'preview': snippet['preview']
        })
    
    return jsonify(snippets_list)

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
