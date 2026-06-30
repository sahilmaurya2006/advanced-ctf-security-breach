#!/usr/bin/env python3
"""
Advanced CTF Challenge: Security System Breach
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import jwt
import sqlite3
import os
import base64
import hashlib
from datetime import datetime, timedelta
from Crypto.Cipher import AES
import json

app = Flask(__name__)
app.secret_key = "supersecretkey12345"

def encrypt_aes(plaintext, key):
    cipher = AES.new(key, AES.MODE_CBC)
    iv = cipher.iv
    ciphertext = cipher.encrypt(plaintext.encode().ljust(32))
    return base64.b64encode(iv + ciphertext).decode()

def init_db():
    conn = sqlite3.connect('ctf.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)''')
    users = [
        ('admin', hashlib.md5('Admin@2024'.encode()).hexdigest(), 'admin'),
        ('user', hashlib.md5('User123'.encode()).hexdigest(), 'user'),
    ]
    for username, password, role in users:
        c.execute('INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)',
                 (username, password, role))
    conn.commit()
    conn.close()

if not os.path.exists('ctf.db'):
    init_db()

SECRET_KEY_HEX = "3b6ba8f92d8c4e7a1f5b9c2d6e8a4f3b"
SECRET_KEY_BYTES = bytes.fromhex(SECRET_KEY_HEX)
ADMIN_TOKEN_SECRET = "jwt_secret_key_weak"

FLAG = "CTF{Security_Breach_2024}"

@app.route('/')
def index():
    return '''<!DOCTYPE html><html><head><title>Security Portal</title>
    <style>body{font-family:Arial;background:#1a1a1a;color:#00ff00;margin:20px}
    .info{background:#222;padding:15px;border-left:4px solid #00ff00;margin:10px 0}
    code{background:#0a0a0a;padding:2px 6px}a{color:#00ff00}</style></head>
    <body><div style="max-width:800px;margin:0 auto"><h1>🔐 Secure Access Portal</h1>
    <div class="info"><strong>Status:</strong> OPERATIONAL</div>
    <div class="info">Key Pattern: <code>3b6ba8f92d8c4e7a[REDACTED]</code></div>
    <div class="info">Cipher: AES-256-CBC</div>
    <div class="info"><a href="/login">Login</a></div></div></body></html>'''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    conn = sqlite3.connect('ctf.db')
    c = conn.cursor()
    password_hash = hashlib.md5(password.encode()).hexdigest()
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password_hash}'"
    
    try:
        c.execute(query)
        user = c.fetchone()
        conn.close()
        
        if user:
            token = jwt.encode({
                'user_id': user[0],
                'username': user[1],
                'role': user[3],
                'exp': datetime.utcnow() + timedelta(hours=1)
            }, ADMIN_TOKEN_SECRET, algorithm='HS256')
            
            session['token'] = token
            session['username'] = user[1]
            session['role'] = user[3]
            return redirect('/admin')
        else:
            return render_template('login.html', error='Invalid credentials')
    except Exception as e:
        conn.close()
        return render_template('login.html', error=f'Error: {str(e)[:50]}')

@app.route('/admin')
def admin():
    if 'token' not in session:
        return redirect('/login')
    return render_template('admin.html', username=session.get('username'))

@app.route('/api/config')
def api_config():
    if 'token' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    config = {'api_key': 'sk_live_abcd1234efgh', 'db_pass': 'SecurePass@2024'}
    encrypted = encrypt_aes(json.dumps(config), SECRET_KEY_BYTES)
    return jsonify({'status': 'encrypted', 'data': encrypted})

@app.route('/api/status')
def api_status():
    return jsonify({'status': 'online', 'encryption_key_start': '3b6ba8f92d8c4e7a'})

@app.route('/api/verify', methods=['GET', 'POST'])
def verify_flag():
    flag = request.args.get('flag', '') or request.form.get('flag', '')
    if flag == FLAG:
        return jsonify({'status': 'success', 'message': '🎉 Flag verified!'})
    return jsonify({'status': 'failed', 'message': 'Incorrect'})

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
