import sqlite3
import json
import os
from .models import User, Chat, Message
from config.settings import DATABASE_FILE

db = sqlite3.connect(DATABASE_FILE)
db.row_factory = sqlite3.Row
''' you don't need these functions
def ensure_directories():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(CHATS_DIR, exist_ok=True)
'''

def load_users() -> dict:
    rows = db.execute("SELECT * FROM users").fetchall()
    users = {}
    for row in rows:
        login = row['login']
        users[login] = {
            "login": login,
            "public_key": row['public_key'],
            "password_hash": row['password_hash'],
            "salt": row['salt'],
            "created_at": row['created_at'],
            "chats": []
        }
    return users

def load_chat(chat_id: str) -> dict | None:
    chat_row = db.execute("SELECT * FROM chats WHERE id = ?", (chat_id,)).fetchone()
    if not chat_row:
        return None
    
    chat = dict(chat_row)
    
    participants = db.execute("SELECT user_login FROM participants WHERE chat_id = ?", (chat_id,)).fetchall()
    chat['participants'] = [p['user_login'] for p in participants]
    
    messages = db.execute('''
        SELECT id, from_user, encrypted_alice, encrypted_bob, timestamp
        FROM messages WHERE chat_id = ? ORDER BY timestamp
    ''', (chat_id,)).fetchall()
    
    chat['messages'] = [
        {
            'id': m['id'],
            'from_user': m['from_user'],
            'encrypted': {
                'alice': m['encrypted_alice'],
                'bob': m['encrypted_bob']
            },
            'timestamp': m['timestamp']
        }
        for m in messages
    ]
    
    return chat

def save_users(users: dict):
    for login, data in users.items():
        db.execute('''
            INSERT OR REPLACE INTO users (login, public_key, password_hash, salt, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (login, data.get('public_key'), data['password_hash'], data['salt'], data.get('created_at')))
    db.commit()

def save_chat(chat_id: str, chat_data: dict):
    # 1. сохраняем чат
    db.execute('''
        INSERT OR REPLACE INTO chats (id, name, type, created_at)
        VALUES (?, ?, ?, ?)
    ''', (chat_id, chat_data.get('name'), chat_data.get('type'), chat_data.get('created_at')))
    
    # 2. обновляем участников
    db.execute("DELETE FROM participants WHERE chat_id = ?", (chat_id,))
    for participant in chat_data.get('participants', []):
        db.execute('''
            INSERT INTO participants (chat_id, user_login)
            VALUES (?, ?)
        ''', (chat_id, participant))
    
    # 3. сохраняем сообщения
    for msg in chat_data.get('messages', []):
        db.execute('''
            INSERT OR REPLACE INTO messages (id, chat_id, from_user, encrypted_alice, encrypted_bob, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (msg['id'], chat_id, msg['from_user'], msg['encrypted']['alice'], msg['encrypted']['bob'], msg['timestamp']))
    
    # 4. сохраняем изменения
    db.commit()

def get_file_by_id(file_id: str) -> dict | None:
    """
    Ищет файл по ID в сообщениях всех чатов.
    Возвращает словарь с информацией о файле или None.
    """
    rows = db.execute('''
        SELECT chat_id, from_user, timestamp, encrypted_alice, encrypted_bob
        FROM messages
        WHERE id = ?
    ''', (file_id,)).fetchall()
    
    if not rows:
        return None
    
    # Предполагаем, что файл хранится как отдельное сообщение
    row = rows[0]
    return {
        "id": row['id'],
        "chat_id": row['chat_id'],
        "from_user": row['from_user'],
        "timestamp": row['timestamp'],
        "encrypted": {
            "alice": row['encrypted_alice'],
            "bob": row['encrypted_bob']
        }
    }
