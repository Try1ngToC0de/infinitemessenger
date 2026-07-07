from flask import request, jsonify
from core.storage import load_users, save_users, load_chat
import uuid
import datetime

def get_invitations(login):
    """Получение всех приглашений пользователя"""
    users = load_users()
    user = users.get(login)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    invitations = user.get('invitations', [])
    return jsonify({
        "success": True,
        "invitations": invitations
    }), 200

def send_invitation(login):
    """
    Отправка приглашения в чат
    Ожидает JSON: {"chat_id": "...", "chat_name": "...", "to_user": "..."}
    """
    data = request.json
    chat_id = data.get('chat_id')
    chat_name = data.get('chat_name')
    to_user = data.get('to_user')
    
    if not all([chat_id, chat_name, to_user]):
        return jsonify({"error": "chat_id, chat_name, and to_user required"}), 400
    
    users = load_users()
    if to_user not in users:
        return jsonify({"error": "User not found"}), 404
    
    # Проверяем, что пользователь не в чате
    if 'chats' in users[to_user]:
        for chat in users[to_user]['chats']:
            if chat.get('id') == chat_id:
                return jsonify({"error": "User already in chat"}), 409
    
    invitation = {
        "id": str(uuid.uuid4()),
        "chatId": chat_id,
        "chatName": chat_name,
        "fromUser": login,
        "timestamp": datetime.datetime.now().isoformat(),
        "status": "pending"
    }
    
    if 'invitations' not in users[to_user]:
        users[to_user]['invitations'] = []
    users[to_user]['invitations'].append(invitation)
    save_users(users)
    
    return jsonify({"success": True, "invitation": invitation}), 201

def accept_invitation(login):
    """Принятие приглашения"""
    data = request.json
    invitation_id = data.get('invitation_id')
    
    if not invitation_id:
        return jsonify({"error": "invitation_id required"}), 400
    
    users = load_users()
    user = users.get(login)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    invitations = user.get('invitations', [])
    invitation = next((inv for inv in invitations if inv.get('id') == invitation_id), None)
    
    if not invitation:
        return jsonify({"error": "Invitation not found"}), 404
    
    # Добавляем чат пользователю
    chat_id = invitation.get('chatId')
    chat_name = invitation.get('chatName')
    
    if 'chats' not in user:
        user['chats'] = []
    user['chats'].append({
        "id": chat_id,
        "name": chat_name,
        "type": "group",
        "created": datetime.datetime.now().isoformat()
    })
    
    # Обновляем статус приглашения
    for inv in user['invitations']:
        if inv.get('id') == invitation_id:
            inv['status'] = 'accepted'
    
    # Добавляем пользователя в участники чата
    chat_data = load_chat(chat_id)
    if chat_data:
        if 'participants' not in chat_data:
            chat_data['participants'] = []
        if login not in chat_data['participants']:
            chat_data['participants'].append(login)
        from core.storage import save_chat
        save_chat(chat_id, chat_data)
    
    save_users(users)
    return jsonify({"success": True}), 200

def decline_invitation(login):
    """Отклонение приглашения"""
    data = request.json
    invitation_id = data.get('invitation_id')
    
    if not invitation_id:
        return jsonify({"error": "invitation_id required"}), 400
    
    users = load_users()
    user = users.get(login)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if 'invitations' in user:
        user['invitations'] = [inv for inv in user['invitations'] if inv.get('id') != invitation_id]
        save_users(users)
    
    return jsonify({"success": True}), 200