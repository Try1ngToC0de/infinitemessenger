# инициализирую датабазу
import sqlite3
from config.settings import DATABASE_FILE

db = sqlite3.connect(DATABASE_FILE)
the_most = db.cursor()

tab = ["users", "chats", "participants", "messages", "files"]

the_most.executescript(f'''
	CREATE TABLE IF NOT EXISTS {tab[0]} (
    	login TEXT PRIMARY KEY,
    	public_key TEXT,
    	password_hash TEXT NOT NULL,
    	salt TEXT NOT NULL,
    	created_at TEXT
	);
	CREATE TABLE IF NOT EXISTS {tab[1]} (
    	id TEXT PRIMARY KEY,
    	name TEXT,
    	type TEXT,
    	created_at TEXT
	);
	CREATE TABLE IF NOT EXISTS {tab[2]} (
    	chat_id TEXT REFERENCES chats(id) ON DELETE CASCADE,
    	user_login TEXT REFERENCES users(login) ON DELETE CASCADE,
    	PRIMARY KEY (chat_id, user_login)
	);
	CREATE TABLE IF NOT EXISTS {tab[3]} (
    	id TEXT PRIMARY KEY,
    	chat_id TEXT REFERENCES chats(id) ON DELETE CASCADE,
    	from_user TEXT REFERENCES users(login) ON DELETE CASCADE,
    	encrypted_alice TEXT,
    	encrypted_bob TEXT,
    	timestamp TEXT
	);
	CREATE TABLE IF NOT EXISTS {tab[4]} (
    	id TEXT PRIMARY KEY,
    	chat_id TEXT REFERENCES chats(id) ON DELETE CASCADE,
    	uploaded_by TEXT REFERENCES users(login) ON DELETE CASCADE,
    	encrypted_paths TEXT NOT NULL,
    	timestamp TEXT
	);
'''
)

db.commit()
db.close()