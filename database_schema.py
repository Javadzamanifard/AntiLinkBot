import sqlite3

conn = sqlite3.connect('database.db', check_same_thread=False)
cursor = conn.cursor()

# ------------------ ایجاد جدول کاربران ------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    white TEXT NOT NULL DEFAULT 'False',
    warns INTEGER NOT NULL DEFAULT 0
)
""")

# ------------------ ایجاد جدول حالت لینک ------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS link_mode (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mode TEXT NOT NULL DEFAULT 'delete'
)
""")

# ------------------ اطمینان از وجود حداقل یک ردیف در link_mode ------------------
cursor.execute("""
INSERT OR IGNORE INTO link_mode (id, mode)
VALUES (1, 'delete')
""")

# ------------------ ذخیره تغییرات و بستن ------------------
conn.commit()
conn.close()

print("✅ دیتابیس با موفقیت ساخته شد و آماده است.")
