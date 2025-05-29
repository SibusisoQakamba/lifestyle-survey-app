import sqlite3

DATABASE = 'survey_data.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    with open('schema.sql', 'r') as f:
        cursor.executescript(f.read())
    conn.commit()
    conn.close()
    print("Database initialized.")

if __name__ == '__main__':
    init_db()