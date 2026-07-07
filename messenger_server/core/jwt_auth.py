import jwt
import datetime
import secrets
import os
from typing import Optional, Dict, Any, cast
from dotenv import load_dotenv

load_dotenv('D:/InfiniteServer/.env')

SECRET_KEY = os.getenv('JWT_SECRET_KEY')
REFRESH_SECRET = os.getenv('JWT_REFRESH_SECRET')

if not SECRET_KEY or not REFRESH_SECRET:
    raise ValueError("JWT_SECRET_KEY and JWT_REFRESH_SECRET must be set in .env")

# Убеждаем Pyright, что ключи точно строки (не None)
SECRET_KEY = cast(str, SECRET_KEY)
REFRESH_SECRET = cast(str, REFRESH_SECRET)

# Настройки времени жизни токенов
ACCESS_TOKEN_EXPIRE_DAYS = 7
REFRESH_TOKEN_EXPIRE_DAYS = 30

def generate_access_token(user_login: str) -> str:
    """Генерирует JWT-токен доступа"""
    payload = {
        'login': user_login,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS),
        'iat': datetime.datetime.utcnow(),
        'type': 'access'
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def generate_refresh_token(user_login: str) -> str:
    """Генерирует refresh-токен с увеличенным сроком жизни"""
    payload = {
        'login': user_login,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        'iat': datetime.datetime.utcnow(),
        'type': 'refresh',
        'jti': secrets.token_hex(16)
    }
    return jwt.encode(payload, REFRESH_SECRET, algorithm='HS256')

def decode_token(token: str, secret_key: str) -> Optional[Dict[str, Any]]:
    """Декодирует и проверяет токен"""
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def validate_access_token(token: str) -> Optional[str]:
    """Валидирует access-токен и возвращает логин пользователя"""
    payload = decode_token(token, SECRET_KEY)
    if payload and payload.get('type') == 'access':
        return payload.get('login')
    return None

def validate_refresh_token(token: str) -> Optional[str]:
    """Валидирует refresh-токен и возвращает логин пользователя"""
    payload = decode_token(token, REFRESH_SECRET)
    if payload and payload.get('type') == 'refresh':
        return payload.get('login')
    return None
