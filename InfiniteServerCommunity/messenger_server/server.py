from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from functools import wraps
from handlers import auth, chats, messages, files, invitations
from core.jwt_auth import validate_access_token

# ========== декоратор для защиты эндпоинтов ==========
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({"error": "Token missing or invalid"}), 401
        
        token = token.split(' ')[1]
        login = validate_access_token(token)
        if not login:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        return f(login, *args, **kwargs)
    return decorated

# ========== создание приложения ==========
def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    logging.basicConfig(level=logging.INFO)

    # ===== пбуличные эндпоинты =====
    app.add_url_rule('/api/register', view_func=auth.register, methods=['POST'])
    app.add_url_rule('/api/login', view_func=auth.login, methods=['POST'])
    app.add_url_rule('/api/user/set_public_key', view_func=auth.set_public_key, methods=['POST'])
    app.add_url_rule('/api/refresh', view_func=auth.refresh_token, methods=['POST'])

    # ===== защищённые эндпоинты =====
    app.add_url_rule('/api/logout', view_func=auth.logout, methods=['POST'])
    
    app.add_url_rule('/api/chats', view_func=token_required(chats.create_chat), methods=['POST'])
    app.add_url_rule('/api/chats/<chat_id>', view_func=token_required(chats.get_chat), methods=['GET'])
    app.add_url_rule('/api/chats/user', view_func=token_required(chats.get_user_chats), methods=['GET'])
    app.add_url_rule('/api/chats/add', view_func=token_required(chats.add_chat_to_user), methods=['POST'])
    app.add_url_rule('/api/chats/remove', view_func=token_required(chats.remove_chat_from_user), methods=['POST'])
    app.add_url_rule('/api/chats/<chat_id>/participants', view_func=token_required(chats.get_participants), methods=['GET'])

    app.add_url_rule('/api/messages', view_func=token_required(messages.send_message), methods=['POST'])
    app.add_url_rule('/api/messages/<chat_id>', view_func=token_required(messages.get_messages), methods=['GET'])

    app.add_url_rule('/api/files/upload', view_func=token_required(files.upload_file), methods=['POST'])
    app.add_url_rule('/api/files/<file_id>', view_func=files.download_file, methods=['GET'])

    app.add_url_rule('/api/invitations', view_func=token_required(invitations.get_invitations), methods=['GET'])
    app.add_url_rule('/api/invitations/send', view_func=token_required(invitations.send_invitation), methods=['POST'])
    app.add_url_rule('/api/invitations/accept', view_func=token_required(invitations.accept_invitation), methods=['POST'])
    app.add_url_rule('/api/invitations/decline', view_func=token_required(invitations.decline_invitation), methods=['POST'])

    # ===== получение публичного ключа =====
    app.add_url_rule('/api/user/public_key', view_func=token_required(auth.get_user_public_key), methods=['POST'])

    # ===== тестовые эндпоинты =====
    @app.route('/')
    def root():
        return {"message": "Infinite Messenger API is running"}, 200

    @app.route('/api/test')
    def test():
        return {"status": "ok", "message": "API работает"}, 200
    
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    return app
