import sqlite3

try:
    conn = sqlite3.connect('loansi.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM usuarios WHERE username='hpsupersu'")
    user = cursor.fetchone()
    if user:
        print(f"User found: {user[0]}")
    else:
        print("User hpsupersu NOT found")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
