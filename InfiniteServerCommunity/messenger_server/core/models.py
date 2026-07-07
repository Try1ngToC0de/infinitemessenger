from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict

@dataclass
class User:
    login: str
    public_key: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    chats: List[str] = field(default_factory=list)

@dataclass
class Chat:
    id: str
    name: str
    type: str  # 'single' или 'group'
    participants: List[str]
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_message: Optional[Dict] = None

@dataclass
class Message:
    id: str
    chat_id: str
    from_user: str
    encrypted: Dict[str, str]  # { "login": "зашифрованный_текст", ... }
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
