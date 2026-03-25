from werkzeug.security import generate_password_hash
import sqlite3

master_password="vary_sacure"
secure_hash=generate_password_hash(master_password)

stud_password="root@123"
stud_hash=generate_password_hash(stud_password)

connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ('admin_user', secure_hash, 'admin'))

cur.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ('student_Summit', stud_hash, 'student'))

student_id = cur.lastrowid

cur.execute("INSERT INTO tasks (user_id, title, category, user_name) VALUES (?, ?, ?, ?)",
            (student_id, 'Complete Lab 1', 'School', 'Summit'))

connection.commit()
connection.close()

print("Success: database.db has been created!")
print(f"Master password: {master_password}\nStud password: {stud_password}")

