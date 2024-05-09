import sqlite3
import my_config
path = my_config.rk_path


def create_database():
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            payment_id INTEGER,
            user_id INTEGER,
            status INTEGER,
            link TEXT
        )
    ''')
    conn.commit()
    conn.close()

def count_payment_ids() -> int:
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(payment_id) FROM payments')
    count = cursor.fetchone()[0]
    conn.close()
    return count

def add_payment_user(payment_id: int, user_id: int):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO payments (payment_id, user_id) VALUES (?, ?)', (payment_id, user_id))
    conn.commit()
    conn.close()

def set_status_link(payment_id: int, status: int, link: str):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute('UPDATE payments SET status = ?, link = ? WHERE payment_id = ?', (status, link, payment_id))
    conn.commit()
    conn.close()
