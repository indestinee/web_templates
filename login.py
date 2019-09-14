import flask, time, re, pickle

from tools import add_log, get_cur_time
from database import db
from web import app, html

re_all = re.compile(r'^.*$')
re_normal = re.compile(r'^\w+$')

valid_code = lambda x: db.count('code', limitation={
    'code=': valid_code,
    'time>': time.time(),
})

def check_param(param, name, *, pattern=re_normal, min_len=6, max_len=32):
    if len(param) < min_len or len(param) > max_len:
        return False, '{}\'s length should be within [{}, {}].'.format(
            name, min_len, max_len)
    if pattern.match(param):
        return True, ''
    return False, 'Illegal charactor found!'


def login(username='', password=''):
    users = db.select('user', limitation={'username=': username})
    if len(users) == 0: return False, 'Invalid username!'
    user, = users
    if password != user['password']: return False, 'Invalid password!'

    flask.session['login'] = {
        'id': user['id'],
        'username': username,
    }
    add_log('{} login from {} at {} {}.'.format(
        username, flask.request.remote_addr, 
        get_cur_time(), time.tzname[0],
    ), user_id=user['id'])
    return True, 'Login successfully!'
 

def register(username='', password='', code='', login="off"):
    res, msg = check_param(username, 'Username',
                           pattern=re_normal, min_len=2, max_len=32)

    if not res:
        return False, msg

    res, msg = check_param(password, 'Password',
                           pattern=re_all, min_len=6, max_len=32)
    if not res:
        return False, msg

    if not valid_code(code):
        return False, 'Invalid invitation code.'

    try:
        res = db.insert('user', data={
            'username': username,
            'password': password,
            'code': code,
            'level': 0,
        })
        user, = db.select('user', limitation={'username=': username})
        add_log('{} register from {} at {} {}.'.format(
            username, flask.request.remote_addr,
            get_cur_time(), time.tzname[0]
        ), user_id=user['id'])
    except Exception as e:
        return False, '\'{}\' already exists.'.format(username)

    status, msg = True, 'Register successfully!'
    if login == 'on':
        status, msg = login(username, password)
    return status, msg
