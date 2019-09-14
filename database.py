from eic_utils.database import DataBase
import os, time, base64

random_str = lambda n: base64.b64encode(os.urandom(n)).decode('utf-8')


db = DataBase('data/data.db')
db.create_table('user', [
    'id INTEGER PRIMARY KEY AUTOINCREMENT',
    'username TEXT UNIQUE NOT NULL',
    'password TEXT NOT NULL',
    'level INTEGER',
])
db.create_table('log', [
    'id INTEGER PRIMARY KEY AUTOINCREMENT',
    'content TEXT',
    'user_id INTEGER',
    'time FLOAT',
    'FOREIGN KEY (user_id) REFERENCES user(id)',
])
db.create_table('dashboard', [
    'id INTEGER PRIMARY KEY AUTOINCREMENT',
    'data BLOB',
    'time DOUBLE',
])
db.create_table('code', [
    'id INTEGER PRIMARY KEY AUTOINCREMENT',
    'code TEXT',
    'time DOUBLE',
])
db.create_table('download', [
    'id INTEGER PRIMARY KEY AUTOINCREMENT',
    'url TEXT',
    'type TEXT',
    'path TEXT',
    'time DOUBLE',
    'status INT',
])

users = [{
    'username': 'admin',
    'password': random_str(16),
    'level': 100,
}]

codes = [{
    'code': random_str(16),
    'time': time.time() + 86400,
}]
db.insert('code', codes, force=True)
db.insert('user', users, force=True)

print(users)
print(codes)
