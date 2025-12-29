import sqlite3

conn = sqlite3.connect("database.db")
cur = conn.cursor()

# Users table
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT,
    role TEXT
)
""")

# Leave requests table
cur.execute("""
CREATE TABLE IF NOT EXISTS leave_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student TEXT,
    reason TEXT,
    file TEXT,
    attendance INTEGER,
    instructor_status TEXT,
    hod_status TEXT
)
""")

# Insert demo users
cur.executemany("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", [
    ("student1", "1234", "student"),
    ("inst1", "1234", "instructor"),
    ("hod1", "1234", "hod")
])

conn.commit()
conn.close()
print("Database created successfully")
