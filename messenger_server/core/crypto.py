import hashlib
import secrets
import base64
import hashlib
from typing import Tuple, Optional
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from cryptography.hazmat.backends import default_backend

def sha256(message: str) -> str:
    """Вычисляет SHA-256 хеш от строки (для совместимости со старыми паролями)"""
    return hashlib.sha256(message.encode()).hexdigest()

# ==================== ГЕНЕРАЦИЯ КЛЮЧЕЙ ====================
def generate_key_pair() -> Tuple[str, str]:
    """
    Генерирует пару RSA-ключей (приватный и публичный)
    Возвращает: (private_key_pem, public_key_pem) в формате строк
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    
    # Сериализуем ключи в PEM-формат
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode()
    
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()
    
    return private_pem, public_pem

# ==================== ШИФРОВАНИЕ И ДЕШИФРОВАНИЕ ====================
def encrypt_message(message: str, public_key_pem: str) -> str:
    """Шифрует сообщение публичным ключом (RSA)"""
    # Загружаем ключ и явно указываем тип RSAPublicKey
    public_key: RSAPublicKey = serialization.load_pem_public_key(
        public_key_pem.encode(),
        backend=default_backend()
    )  # type: ignore
    
    encrypted = public_key.encrypt(
        message.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return base64.b64encode(encrypted).decode()

def decrypt_message(encrypted_b64: str, private_key_pem: str) -> str:
    """Дешифрует сообщение приватным ключом (RSA)"""
    # Загружаем ключ и явно указываем тип RSAPrivateKey
    private_key: RSAPrivateKey = serialization.load_pem_private_key(
        private_key_pem.encode(),
        password=None,
        backend=default_backend()
    )  # type: ignore
    
    encrypted = base64.b64decode(encrypted_b64)
    decrypted = private_key.decrypt(
        encrypted,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted.decode()

# ==================== ХЕШИРОВАНИЕ ПАРОЛЕЙ ====================
def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """
    Хеширует пароль с солью (PBKDF2)
    Возвращает: (hash, salt) — оба в hex-формате
    """
    if salt is None:
        salt = secrets.token_hex(16)
    
    hash_obj = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode(),
        salt.encode(),
        100000
    )
    return hash_obj.hex(), salt

def verify_password(password: str, hash_hex: str, salt: str) -> bool:
    """Проверяет пароль по хешу и соли"""
    new_hash, _ = hash_password(password, salt)
    return new_hash == hash_hex

# ==================== ПРОВЕРКА КОРРЕКТНОСТИ ====================
if __name__ == "__main__":
    print("🔐 Тестируем crypto.py...")
    
    # Тест ключей
    priv, pub = generate_key_pair()
    print(f"✅ Ключи сгенерированы (приватный: {len(priv)} симв., публичный: {len(pub)} симв.)")
    
    # Тест шифрования
    msg = "Привет, это секретное сообщение!"
    encrypted = encrypt_message(msg, pub)
    decrypted = decrypt_message(encrypted, priv)
    
    if msg == decrypted:
        print(f"✅ Шифрование работает: '{msg}' -> '{decrypted}'")
    else:
        print(f"❌ Ошибка шифрования!")
    
    # Тест хеширования
    password = "my_secret_pass"
    hash_hex, salt = hash_password(password)
    print(f"✅ Хеш пароля: {hash_hex[:16]}... (соль: {salt[:8]}...)")
    
    is_valid = verify_password(password, hash_hex, salt)
    print(f"✅ Проверка пароля: {'успешна' if is_valid else 'провалена'}")
