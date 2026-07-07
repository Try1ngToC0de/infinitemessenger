import os

# Базовые пути
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
CHATS_DIR = os.path.join(DATA_DIR, 'chats')
FILES_DIR = os.path.join(DATA_DIR, 'files')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
DATABASE_FILE = os.path.join(DATA_DIR, 'messenger.db')

# Настройки сервера
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 7089
DEBUG = True  # Для разработки

# Настройки безопасности
SALT_LENGTH = 16
HASH_ITERATIONS = 100000
TOKEN_EXPIRE_HOURS = 24