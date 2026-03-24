
import sqlite3

connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

#cur = connection.cursor()
#cur.execute("INSERT INTO tasks (title, category) VALUES (?, ?)",('Finish Figma Design', 'School'))

connection.commit()
connection.close()

print("Success: database.db has been created!")

