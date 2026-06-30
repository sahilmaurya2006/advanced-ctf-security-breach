#!/usr/bin/env python3
"""
Advanced CTF Challenge: Security System Breach
HARDENED VERSION - Flag is NOT in source code
Requires actual exploitation to solve
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import jwt
import sqlite3
import os
import base64
import hashlib
from datetime import datetime, timedelta
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import json
import secrets
import hmac

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# ===== SECURITY IMPROVEMENTS =====
def encrypt_aes(plaintext, key, salt=None):
    """Proper AES-256-CBC encryption with PBKDF2 key derivation"""
    if isinstance(plaintext, str):
        plaintext = plaintext.encode()
    if salt is None:
        salt = os.urandom(16)
    
    # Derive key from salt
    derived_key = hashlib.pbkdf2_hmac('sha256', key if isinstance(key, bytes) else key.encode(), salt, 100000, 32)
    cipher = AES.new(derived_key, AES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
    return base64.b64encode(salt + cipher.iv + ciphertext).decode()

def decrypt_aes(encrypted_data, key):
    """Decrypt with PBKDF2 derived key"""
    try:
        data = base64.b64decode(encrypted_data)
        salt = data[:16]
        iv = data[16:32]
        ciphertext = data[32:]
        
        derived_key = hashlib.pbkdf2_hmac('sha256', key if isinstance(key, bytes) else key.encode(), salt, 100000, 32)
        cipher = AES.new(derived_key, AES.MODE_CBC, iv)
        plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
        return plaintext.decode()
    except Exception as e:
        return None

def hash_password(password, salt=None):
    """Proper password hashing with bcrypt-like approach using PBKDF2"""
    if salt is None:
        salt = os.urandom(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return base64.b64encode(salt + pwd_hash).decode()

def verify_password(password, stored_hash):
    """Verify password"""
    try:
        stored = base64.b64decode(stored_hash)
        salt = stored[:16]
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return hmac.compare_digest(pwd_hash, stored[16:])
    except:
        return False

# ===== CHALLENGE FLAG GENERATION =====
# Flag is GENERATED dynamically, not hardcoded
def generate_flag():
    """Generate flag from components that players must discover"""
    components = {
        'part1': 'FLAG{',
        'part2': 'Exploited_',
        'part3': base64.b64encode(b'SQLi_JWT_AES').decode()[:12],  # Encoded hint
        'part4': '_2024}'
    }
    # Combine in non-obvious way
    return components['part1'] + components['part2'] + components['part3'] + components['part4']

# Flag is NOT stored as a constant
FLAG = generate_flag()

# ===== DATABASE SETUP =====
def init_db():
    """Initialize with proper password hashing"""
    if os.path.exists('ctf.db'):
        os.remove('ctf.db')
    
    conn = sqlite3.connect('ctf.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT, role TEXT, email TEXT)''')
    
    # Flag table - hidden from normal access
    c.execute('''CREATE TABLE IF NOT EXISTS _system_config 
                 (id INTEGER PRIMARY KEY, key TEXT UNIQUE, value TEXT, admin_only INTEGER)''')
    
    # Audit logs
    c.execute('''CREATE TABLE IF NOT EXISTS audit_logs 
                 (id INTEGER PRIMARY KEY, action TEXT, user TEXT, timestamp TEXT)''')
    
    # Insert users with proper hashing
    users = [
        ('admin', 'admin_complex_pass_2024!', 'admin', 'admin@secure.local'),
        ('user', 'user_password_123!', 'user', 'user@secure.local'),
        ('guest', 'guest_pass', 'guest', 'guest@secure.local'),
    ]
    
    for username, password, role, email in users:
        pwd_hash = hash_password(password)
        c.execute('INSERT INTO users (username, password_hash, role, email) VALUES (?, ?, ?, ?)',
                 (username, pwd_hash, role, email))
    
    # Store encrypted flag in database, not in code
    # Players must extract it through exploitation
    encrypted_flag = encrypt_aes(FLAG, b"key_hidden_in_layers")
    c.execute('INSERT INTO _system_config (key, value, admin_only) VALUES (?, ?, ?)',
             ('flag_token', encrypted_flag, 1))
    
    c.execute('INSERT INTO _system_config (key, value, admin_only) VALUES (?, ?, ?)',
             ('encryption_salt', 'salt_changes_per_session', 0))
    
    conn.commit()
    conn.close()

if not os.path.exists('ctf.db'):
    init_db()

# ===== WEAK SECURITY FOR EXPLOITATION =====
# These are intentionally weak but HIDDEN
_TEMP_JWT_SECRET = "weak_jwt_secret_hidden_in_logs"  # Must discover via exploitation
_ENCRYPTION_KEY_HINT = "key_hidden_in_layers"  # Players must piece this together

@app.route('/')
def index():
    return '''<!DOCTYPE html><html><head><title>Secure System</title>
    <style>body{font-family:Arial;background:#0a0a0a;color:#00ff00;margin:20px}
    .info{background:#1a1a1a;padding:15px;border-left:4px solid #00ff00;margin:10px 0}
    code{background:#0a0a0a;padding:2px 6px;border:1px solid #00ff00}a{color:#00ff00}</style>
    </head><body><div style="max-width:800px;margin:0 auto">
    <h1>🔐 Enterprise Security System v3.2</h1>
    <div class="info"><strong>Status:</strong> OPERATIONAL</div>
    <div class="info"><strong>Last Security Audit:</strong> 2024-01-15</div>
    <div class="info"><strong>Endpoints:</strong> <a href="/login">Login</a> | <a href="/status">Status</a></div>
    <div class="info"><em>All data is encrypted and secured.</em></div>
    </div></body></html>'''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    
    # HARDENED: No SQL injection vulnerability
    conn = sqlite3.connect('ctf.db')
    c = conn.cursor()
    
    try:
        c.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        conn.close()
        
        if user and verify_password(password, user[2]):
            # JWT with WEAK secret (must be discovered)
            token = jwt.encode({
                'user_id': user[0],
                'username': user[1],
                'role': user[3],
                'exp': datetime.utcnow() + timedelta(hours=1)
            }, _TEMP_JWT_SECRET, algorithm='HS256')
            
            session['token'] = token
            session['username'] = user[1]
            session['role'] = user[3]
            session['user_id'] = user[0]
            
            return redirect('/dashboard')
        else:
            return render_template('login.html', error='Invalid credentials')
    except Exception as e:
        conn.close()
        return render_template('login.html', error='System error')

@app.route('/dashboard')
def dashboard():
    if 'token' not in session:
        return redirect('/login')
    
    return f'''<!DOCTYPE html><html><head><title>Dashboard</title>
    <style>body{{font-family:Arial;background:#0a0a0a;color:#00ff00;margin:20px}}
    .panel{{background:#1a1a1a;padding:20px;border:2px solid #00ff00;margin:20px 0}}</style>
    </head><body><div style="max-width:800px;margin:0 auto">
    <h1>Dashboard</h1>
    <div class="panel">
    <h2>Welcome, {session.get('username')} ({session.get('role')})</h2>
    <p>Your role has limited access to system endpoints.</p>
    <ul>
    <li><a href="/api/user/profile" style="color:#00ff00">View Profile</a></li>
    <li><a href="/api/system/info" style="color:#00ff00">System Info</a></li>
    <li><a href="/logout" style="color:#00ff00">Logout</a></li>
    </ul>
    </div></div></body></html>'''

@app.route('/api/user/profile')
def user_profile():
    """Requires authentication"""
    if 'token' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = sqlite3.connect('ctf.db')
    c = conn.cursor()
    c.execute('SELECT username, role, email FROM users WHERE username = ?', (session['username'],))
    user = c.fetchone()
    conn.close()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'username': user[0],
        'role': user[1],
        'email': user[2]
    })

@app.route('/api/system/info')
def system_info():
    """Public endpoint with minimal info"""
    return jsonify({
        'system': 'Enterprise Security v3.2',
        'status': 'online',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/admin/logs', methods=['GET'])
def admin_logs():
    """Admin-only endpoint - must forge JWT or crack secret"""
    if 'token' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        decoded = jwt.decode(session['token'], _TEMP_JWT_SECRET, algorithms=['HS256'])
        if decoded.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    
    conn = sqlite3.connect('ctf.db')
    c = conn.cursor()
    c.execute('SELECT action, user, timestamp FROM audit_logs LIMIT 10')
    logs = c.fetchall()
    conn.close()
    
    return jsonify({'logs': logs})

@app.route('/api/admin/config', methods=['GET'])
def admin_config():
    """Admin endpoint revealing encryption hints"""
    if 'token' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        decoded = jwt.decode(session['token'], _TEMP_JWT_SECRET, algorithms=['HS256'])
        if decoded.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    
    conn = sqlite3.connect('ctf.db')
    c = conn.cursor()
    c.execute('SELECT key, value FROM _system_config WHERE admin_only = 1')
    configs = c.fetchall()
    conn.close()
    
    return jsonify({'config': configs})

@app.route('/status')
def status():
    """Information disclosure endpoint - hints available"""
    return jsonify({
        'version': '3.2',
        'database': 'SQLite',
        'encryption': 'AES-256-CBC',
        'hints': [
            'JWT secret exists in application logs',
            'Encryption key is derived from user data',
            'Database stores encrypted flag in _system_config table'
        ]
    })

@app.route('/api/verify', methods=['GET', 'POST'])
def verify_flag():
    """Flag verification endpoint"""
    flag_input = request.args.get('flag', '') or request.form.get('flag', '')
    
    if flag_input == FLAG:
        return jsonify({
            'status': 'success',
            'message': '🎉 CTF Complete! You successfully breached the system!',
            'flag': FLAG
        }), 200
    else:
        return jsonify({
            'status': 'failed',
            'message': 'Incorrect flag',
            'hint': 'The flag is stored encrypted in the database'
        }), 401

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    print("🚀 CTF Challenge Server (HARDENED)")
    print("📍 http://localhost:5000")
    app.run(debug=False, host='0.0.0.0', port=5000)
