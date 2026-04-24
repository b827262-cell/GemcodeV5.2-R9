import sqlite3
import datetime

DB_NAME = "calculator.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS calculation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            operation VARCHAR(50) NOT NULL,
            operand_a FLOAT NOT NULL,
            operand_b FLOAT NOT NULL,
            result FLOAT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def insert_calculation(operation, operand_a, operand_b, result):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO calculation_history (operation, operand_a, operand_b, result, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (operation, operand_a, operand_b, result, datetime.datetime.utcnow().isoformat()))
    conn.commit()
    inserted_id = cursor.lastrowid
    conn.close()
    return inserted_id

def get_history():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM calculation_history ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
