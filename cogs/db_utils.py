import sqlite3

# Define the path to your SQLite database
DB_PATH = 'conversation_history.db'

def init_db():
    """Initialize the database with the necessary tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversation (
            user_id INTEGER,
            prompt TEXT,
            response TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def insert_conversation(user_id, prompt, response):
    """Insert a conversation entry into the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO conversation (user_id, prompt, response)
        VALUES (?, ?, ?)
    ''', (user_id, prompt, response))
    conn.commit()
    conn.close()

def fetch_conversations(limit=10):
    """Fetch the most recent conversations from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT user_id, prompt, response, timestamp
        FROM conversation
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows
