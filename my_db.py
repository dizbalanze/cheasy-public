import my_config
import sqlite3

db_path = my_config.db_path


def create_db():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS messages ( user_id INTEGER, message TEXT, role TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)')
    c.execute('CREATE TABLE IF NOT EXISTS user_limits ( user_id INTEGER PRIMARY KEY, message_limit INTEGER, registered INTEGER, rating INTEGER)')

    try: c.execute("SELECT review FROM user_limits LIMIT 1")
    except sqlite3.OperationalError: c.execute('''ALTER TABLE user_limits ADD COLUMN review TEXT''')

    conn.commit()
    conn.close()


def get_all_user_ids():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT user_id FROM user_limits")
    user_ids = [row[0] for row in c.fetchall()]
    conn.close()
    return user_ids


def set_user_rating(user_id, rating):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("UPDATE user_limits SET rating = ? WHERE user_id = ?", (rating, user_id))
    conn.commit()
    conn.close()


def add_message_to_db(user_id, message, role):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("INSERT INTO messages (user_id, message, role, timestamp) VALUES (?, ?, ?, CURRENT_TIMESTAMP)", (user_id, message, role))
    conn.commit()
    conn.close()


def count_all_messages(user_id):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM messages WHERE user_id = ? AND role = 'user'", (user_id,))
    count = c.fetchone()[0]
    conn.close()
    return count


def get_user_messages(user_id):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT message, role FROM messages WHERE user_id = ?", (user_id,))
    messages = c.fetchall()

    if not messages: return [{"role": "assistant", "content": 'Здравствуйте! Я ИИ консультант компании Neo Boost. Чем я могу помочь вам сегодня?'}]
    else: return [{"role": role, "content": message} for message, role in messages]


def delete_old_messages(user_id, max_length=6000):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("SELECT SUM(LENGTH(message)) FROM messages WHERE user_id = ?", (user_id,))
    total_length = c.fetchone()[0] or 0

    while total_length > max_length:
        c.execute("SELECT rowid FROM messages WHERE user_id = ? ORDER BY rowid ASC LIMIT 1", (user_id,))
        oldest_message_id = c.fetchone()[0]
        c.execute("DELETE FROM messages WHERE rowid = ?", (oldest_message_id,))
        c.execute("SELECT SUM(LENGTH(message)) FROM messages WHERE user_id = ?", (user_id,))
        total_length = c.fetchone()[0] or 0

    conn.commit()
    conn.close()


def set_user_message_limit(user_id, limit):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO user_limits (user_id, message_limit) VALUES (?, ?)", (user_id, limit))
    conn.commit()
    conn.close()


def get_user_message_limit(user_id):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT message_limit FROM user_limits WHERE user_id = ?", (user_id,))
    limit = c.fetchone()
    conn.close()
    return limit[0] if limit else 0


def set_user_registration_status(user_id, registered):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO user_limits (user_id, message_limit, registered) VALUES (?, 100, 0)", (user_id,))
    c.execute("UPDATE user_limits SET registered = ? WHERE user_id = ?", (int(registered), user_id))
    conn.commit()
    conn.close()


def get_user_registration_status(user_id):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT registered FROM user_limits WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    return bool(result[0]) if result else False


def check_user_exists(user_id):
    try:
        mes_id = int(user_id)
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM user_limits WHERE user_id = ?", (mes_id,))
        result = c.fetchone()
        conn.close()
        return result is not None

    except: return False


def save_user_review(user_id, review):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("UPDATE user_limits SET review = ? WHERE user_id = ?", (review, user_id))
    conn.commit()
    conn.close()
