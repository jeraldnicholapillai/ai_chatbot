import sqlite3

def get_schema():
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    schema = ""
    for (t,) in tables:
        cursor.execute(f"PRAGMA table_info({t})")
        cols = cursor.fetchall()
        schema += f"\nTABLE {t}:\n"
        for col in cols:
            schema += f"  - {col[1]} ({col[2]})\n"

    conn.close()
    return schema
