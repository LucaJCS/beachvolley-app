import sqlite3

# Connettersi al database
conn = sqlite3.connect('sports.db')
cursor = conn.cursor()

# Creazione delle tabelle per ogni sport
cursor.execute('''
CREATE TABLE IF NOT EXISTS beachvolley (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    level TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS tennis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    level TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS calcetto (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    level TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS padel (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    level TEXT NOT NULL
)
''')

# Commit e chiusura della connessione
conn.commit()
conn.close()

print("Tabelle create con successo!")
