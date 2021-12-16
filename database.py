import sqlite3

conn = sqlite3.connect('database2.db')

conn.execute('''CREATE TABLE users(userId TEXT PRIMARY KEY, password TEXT, email TEXT, fullName TEXT)''')
