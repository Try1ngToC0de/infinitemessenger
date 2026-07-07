import datetime
from flask import request, jsonify
from core.storage import load_users, save_users
from core.crypto import hash_password, verify_password, sha256
from core.jwt_auth import generate_access_token, generate_refresh_token, validate_access_token, validate_refresh_token

def get_public_key(login):
    users = load_users()
    user = users.get(login)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "success": True,
        "public_key": user.get('public_key', '')
    }), 200

def register():
    data = request.json
    login = data.get('login')
    password = data.get('password')
    public_key = data.get('public_key')

    if not login or not password:
        return jsonify({"error": "Login and password required"}), 400

    users = load_users()
    if login in users:
        return jsonify({"error": "User already exists"}), 409

    password_hash, salt = hash_password(password)
    
    users[login] = {
        "login": login,
        "public_key": public_key or "",
        "password_hash": password_hash,
        "salt": salt,
        "chats": [],
        "created_at": datetime.datetime.now().isoformat()
    }
    save_users(users)

    access_token = generate_access_token(login)
    refresh_token = generate_refresh_token(login)

    return jsonify({
        "success": True,
        "message": "User registered successfully",
        "public_key": users[login]["public_key"],
        "access_token": access_token,
        "refresh_token": refresh_token,
        "chats": []
    }), 201

def login():
    data = request.json
    login = data.get('login')
    password = data.get('password')

    if not login or not password:
        return jsonify({"error": "Login and password required"}), 400

    users = load_users()
    user = users.get(login)
    if not user:
        return jsonify({"error": "User not found"}), 404

    password_hash = user.get('password_hash', '')
    salt = user.get('salt', '')

    is_valid = False
    
    if salt and verify_password(password, password_hash, salt):
        is_valid = True
    
    elif not salt and password_hash:
        if sha256(password) == password_hash:
            is_valid = True
            new_hash, new_salt = hash_password(password)
            user['password_hash'] = new_hash
            user['salt'] = new_salt
            save_users(users)

    if not is_valid:
        return jsonify({"error": "Invalid password"}), 401

    access_token = generate_access_token(login)
    refresh_token = generate_refresh_token(login)

    return jsonify({
        "success": True,
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "public_key": user.get('public_key', ''),
        "chats": user.get('chats', [])
    }), 200

def refresh_token():
    data = request.json
    refresh_token = data.get('refresh_token')
    
    if not refresh_token:
        return jsonify({"error": "Refresh token required"}), 400
    
    login = validate_refresh_token(refresh_token)
    if not login:
        return jsonify({"error": "Invalid or expired refresh token"}), 401
    
    new_access_token = generate_access_token(login)
    
    return jsonify({
        "success": True,
        "access_token": new_access_token
    }), 200

def logout():
    return jsonify({"success": True, "message": "Logged out"}), 200

def get_user_public_key(login):
    data = request.json
    target_login = data.get('target_login')
    
    if not target_login:
        return jsonify({"error": "target_login required"}), 400
    
    if target_login == login:
        return jsonify({"error": "Cannot request your own public key via this endpoint"}), 400

    users = load_users()
    user = users.get(target_login)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "success": True,
        "public_key": user.get('public_key', '')
    }), 200

def set_public_key(login):
    data = request.json
    public_key = data.get('public_key')
    
    if not public_key:
        return jsonify({"error": "public_key required"}), 400
    
    users = load_users()
    if login not in users:
        return jsonify({"error": "User not found"}), 404
    
    users[login]['public_key'] = public_key
    save_users(users)
    
    return jsonify({"success": True}), 200