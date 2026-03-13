import sqlite3
import os

# Ensure absolute path to avoid "no such table" if run from different cwd
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'attendance.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            day TEXT,
            class_name TEXT,
            section TEXT,
            total_students INTEGER,
            presents INTEGER,
            absents INTEGER,
            percentage REAL,
            UNIQUE(date, class_name, section)
        )
    ''')
    conn.commit()
    conn.close()

def save_attendance(date, day, class_name, section, total_students, presents, absents, percentage):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO attendance (id, date, day, class_name, section, total_students, presents, absents, percentage)
        VALUES ((SELECT id FROM attendance WHERE date=? AND class_name=? AND section=?), ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (date, class_name, section, date, day, class_name, section, total_students, presents, absents, percentage))
    conn.commit()
    conn.close()

def get_attendance(start_date, end_date, class_name=None, section=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = "SELECT date, day, class_name, section, total_students, presents, absents, percentage FROM attendance WHERE date >= ? AND date <= ?"
    params = [start_date, end_date]
    
    if class_name and class_name != "All Classes":
        query += " AND class_name = ?"
        params.append(class_name)
        
    if section and section not in ("Both Section", "All Sections"):
        query += " AND section = ?"
        params.append(section)
        
    query += " ORDER BY date ASC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    columns = ["date", "day", "class_name", "section", "total_students", "presents", "absents", "percentage"]
    return [dict(zip(columns, row)) for row in rows]
