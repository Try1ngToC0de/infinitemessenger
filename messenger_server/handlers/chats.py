from flask import request, jsonify
from core.storage import load_users, save_users, load_chat, save_chat
from core.models import Chat
import uuid
import datetime

def create_chat(login):
    """
    Создание нового чата (защищённый эндпоинт).
    login — текущий пользователь (из JWT).
    Ожидает JSON: {"name": "Chat Name", "type": "group|single", "participants": ["user1", "user2"]}
    """
    data = request.json
    chat_name = data.get('name')
    chat_type = data.get('type', 'group')
    participants = data.get('participants', [])

    # Добавляем создателя в участники, если его там нет
    if login not in participants:
        participants.append(login)

    # Валидация
    if chat_type == 'single':
        if len(participants) != 2:
            return jsonify({"error": "Single chat requires exactly 2 participants"}), 400

        # Проверяем, не существует ли уже такой чат
        users = load_users()
        for other_login in participants:
            if other_login != login:
                for chat in users.get(other_login, {}).get('chats', []):
                    if chat.get('type') == 'single' and chat.get('id'):
                        chat_data = load_chat(chat['id'])
                        if chat_data and set(chat_data.get('participants', [])) == set(participants):
                            return jsonify({
                                "error": "Chat already exists",
                                "chat_id": chat['id'],
                                "chat_name": chat.get('name', '')
                            }), 409
    else:
        if len(participants) < 2:
            return jsonify({"error": "Group chat requires at least 2 participants"}), 400
        if not chat_name:
            return jsonify({"error": "Chat name required for group chat"}), 400

    # Проверяем, что все участники существуют
    users = load_users()
    for user_login in participants:
        if user_login not in users:
            return jsonify({"error": f"User {user_login} not found"}), 404

    # Генерируем ID и создаём чат
    chat_id = str(uuid.uuid4())

    # Для личного чата общее имя не хранится (используется только для отображения у каждого)
    actual_name = chat_name or "Личный чат" if chat_type == 'single' else chat_name

    chat = Chat(
        id=chat_id,
        name=actual_name,
        type=chat_type,
        participants=participants,
        created_at=datetime.datetime.now().isoformat()
    )
    chat_data = chat.__dict__
    chat_data['messages'] = []

    # Сохраняем чат
    save_chat(chat_id, chat_data)

    # Добавляем чат в список чатов каждого участника с ПРАВИЛЬНЫМ отображением
    for user_login in participants:
        if 'chats' not in users[user_login]:
            users[user_login]['chats'] = []

        # Определяем имя для отображения
        if chat_type == 'single':
            # Для личного чата — показываем имя другого участника
            other = [p for p in participants if p != user_login][0]
            display_name = other
        else:
            display_name = chat_name

        # Проверяем, нет ли уже такого чата (на случай, если он уже был добавлен)
        if not any(c.get('id') == chat_id for c in users[user_login]['chats']):
            users[user_login]['chats'].append({
                "id": chat_id,
                "name": display_name,
                "type": chat_type,
                "created": datetime.datetime.now().isoformat()
            })

    save_users(users)

    return jsonify({
        "success": True,
        "chat_id": chat_id,
        "chat": chat_data
    }), 201

def get_chat(chat_id):
    """
    Получение информации о чате и его сообщениях (защищённый эндпоинт).
    """
    chat_data = load_chat(chat_id)
    if not chat_data:
        return jsonify({"error": "Chat not found"}), 404

    return jsonify({
        "id": chat_id,
        "name": chat_data.get('name'),
        "type": chat_data.get('type'),
        "participants": chat_data.get('participants', []),
        "created_at": chat_data.get('created_at'),
        "messages": chat_data.get('messages', [])  # Можно ограничить количество
    }), 200

def get_user_chats(login, target_login=None):
    """
    Получение списка чатов пользователя.
    Если target_login не указан, возвращаем чаты текущего пользователя.
    """
    if not target_login:
        target_login = login  # По умолчанию — текущий пользователь
    
    # Проверяем, что пользователь существует
    users = load_users()
    if target_login not in users:
        return jsonify({"error": "User not found"}), 404
    
    # Если запрашиваем чаты другого пользователя, проверяем права
    if target_login != login:
        # В личном чате можно видеть чаты только свои
        return jsonify({"error": "Access denied"}), 403

    user = users[target_login]
    chats = user.get('chats', [])
    
    # Обогащаем данные чатов (можно добавить последнее сообщение)
    enriched_chats = []
    for chat in chats:
        chat_data = load_chat(chat['id'])
        if chat_data:
            messages = chat_data.get('messages', [])
            last_message = messages[-1] if messages else None
            enriched_chats.append({
                "id": chat['id'],
                "name": chat.get('name'),
                "type": chat.get('type'),
                "created": chat.get('created'),
                "last_message": last_message
            })
    
    return jsonify({
        "success": True,
        "chats": enriched_chats
    }), 200

def add_chat_to_user(login):
    """
    Добавляет чат пользователю (по приглашению).
    Ожидает JSON: {"chat_id": "123", "display_name": "Chat Name", "type": "group"}
    """
    data = request.json
    chat_id = data.get('chat_id')
    display_name = data.get('display_name')
    chat_type = data.get('type', 'group')

    if not chat_id:
        return jsonify({"error": "chat_id required"}), 400

    users = load_users()
    if login not in users:
        return jsonify({"error": "User not found"}), 404

    # Проверяем, что чат существует
    chat_data = load_chat(chat_id)
    if not chat_data:
        return jsonify({"error": "Chat not found"}), 404

    # Проверяем, что пользователь ещё не в чате
    if 'chats' not in users[login]:
        users[login]['chats'] = []
    
    if any(c.get('id') == chat_id for c in users[login]['chats']):
        return jsonify({"error": "User already in chat"}), 409

    # Для личного чата определяем имя для отображения
    if chat_type == 'single':
        # Ищем другого участника (кроме текущего)
        other = [p for p in chat_data.get('participants', []) if p != login]
        display_name = other[0] if other else display_name

    # Добавляем чат в список
    users[login]['chats'].append({
        "id": chat_id,
        "name": display_name or chat_data.get('name', ''),
        "type": chat_type,
        "created": datetime.datetime.now().isoformat()
    })
    
    # Добавляем пользователя в участники чата
    if 'participants' not in chat_data:
        chat_data['participants'] = []
    if login not in chat_data['participants']:
        chat_data['participants'].append(login)
        save_chat(chat_id, chat_data)

    save_users(users)
    return jsonify({"success": True}), 200

def remove_chat_from_user(login):
    """
    Удаляет чат из списка пользователя.
    Ожидает JSON: {"chat_id": "123"}
    """
    data = request.json
    chat_id = data.get('chat_id')

    if not chat_id:
        return jsonify({"error": "chat_id required"}), 400

    users = load_users()
    if login not in users:
        return jsonify({"error": "User not found"}), 404

    user = users[login]
    if 'chats' in user:
        user['chats'] = [c for c in user['chats'] if c.get('id') != chat_id]
        save_users(users)

    return jsonify({"success": True}), 200

def get_participants(login, chat_id):
    """
    Получение списка участников чата (защищённый эндпоинт).
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
        "success": True,
        "participants": chat_data.get('participants', [])
    }), 200