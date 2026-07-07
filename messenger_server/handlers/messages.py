from flask import request, jsonify
from core.storage import load_chat, save_chat
import uuid
import datetime

def send_message(login):
    """
    Отправка сообщения в чат (защищённый эндпоинт).
    login — текущий пользователь (из JWT).
    Ожидает JSON: {"chat_id": "123", "encrypted": {"alice": "...", "bob": "..."}}
    """
    data = request.json
    chat_id = data.get('chat_id')
    encrypted = data.get('encrypted')  # Словарь с зашифрованными сообщениями для каждого участника

    if not chat_id or not encrypted:
        return jsonify({"error": "chat_id and encrypted are required"}), 400

    # Загружаем чат
    chat_data = load_chat(chat_id)
    if not chat_data:
        return jsonify({"error": "Chat not found"}), 404

    # Проверяем, что пользователь является участником чата
    if login not in chat_data.get('participants', []):
        return jsonify({"error": "User is not a participant of this chat"}), 403

    # Создаём сообщение
    message = {
        "id": str(uuid.uuid4()),
        "from_user": login,  # Используем login из JWT
        "encrypted": encrypted,
        "timestamp": datetime.datetime.now().isoformat()
    }

    # Добавляем сообщение в список
    if 'messages' not in chat_data:
        chat_data['messages'] = []
    chat_data['messages'].append(message)

    # Сохраняем обновлённый чат
    save_chat(chat_id, chat_data)

    return jsonify({
        "success": True,
        "message_id": message['id'],
        "timestamp": message['timestamp']
    }), 201

def get_messages(login, chat_id):
    """
    Получение всех сообщений чата (защищённый эндпоинт).
    login — текущий пользователь (из JWT).
    chat_id — ID чата из URL.
    """
    chat_data = load_chat(chat_id)
    if not chat_data:
        return jsonify({"error": "Chat not found"}), 404

    # Проверяем, что пользователь является участником чата
    if login not in chat_data.get('participants', []):
        return jsonify({"error": "Access denied"}), 403

    return jsonify({
        "chat_id": chat_id,
        "messages": chat_data.get('messages', [])
    }), 200
