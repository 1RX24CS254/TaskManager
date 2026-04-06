from werkzeug.security import generate_password_hash
import sqlite3

master_password="vary_sacure"
secure_hash=generate_password_hash(master_password)

stud_password="root@123"
stud_hash=generate_password_hash(stud_password)

prof_pass="1234"
webmaster_pass="5678"

prof_hash=generate_password_hash(prof_pass)
webmaster_hash=generate_password_hash(webmaster_pass)

connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ('admin_user', secure_hash, 'admin'))

cur.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ('student_Summit', stud_hash, 'student'))

cur.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ('professor', prof_hash, 'professor'))

cur.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ('webmaster', prof_hash, 'webmaster'))


student_id = cur.lastrowid

cur.execute("INSERT INTO tasks (user_id, title, category, user_name) VALUES (?, ?, ?, ?)",
            (student_id, 'Complete Lab 1', 'School', 'Summit'))

connection.commit()
connection.close()

print("Success: database.db has been created!")
print(f"Master password: {master_password}\nStud password: {stud_password}")

