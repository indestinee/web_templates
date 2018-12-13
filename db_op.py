from config import db
from getpass import getpass

def insert_admin():
    password = getpass('Password for admin: ')
    db.add_row('user', data={'username': 'admin', 'password': password})

if __name__ == '__main__':
    insert_admin()
