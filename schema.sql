
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
	id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	username TEXT UNIQUE NOT NULL,
	password TEXT NOT NULL,
	role TEXT DEFAULT 'student'
);

CREATE TABLE tasks (
	id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	user_id INTEGER NOT NULL,
	parent_id INTEGER DEFAULT NULL,
	created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	title TEXT NOT NULL,
	description TEXT,
	due_date DATETIME,
	completed_date DATETIME,
	progress_percent INTEGER DEFAULT 0,
	image LONGBLOB,
	user_name TEXT NOT NULL,
	category TEXT,
	priority INTEGER DEFAULT 0,
	is_completed INTEGER DEFAULT 0,
	assigned_role TEXT DEFAULT NULL,
	FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
	FOREIGN KEY (parent_id) REFERENCES tasks(id) ON DELETE CASCADE
);

CREATE INDEX idx_user_tasks ON tasks(user_id);
CREATE INDEX idx_subtasks ON tasks(parent_id);

