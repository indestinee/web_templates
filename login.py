from web import *
import re, pickle


def encrypt(data):
    return data


re_normal = re.compile(r'^\w+$')
re_all = re.compile(r'^.*$')
def check_param(param, *, pattern=re_normal, min_len=6, max_len=32):
    if len(param) < min_len or len(param) > max_len:
        return False, 'length should be within [{}, {}]'.format(\
                min_len, max_len)
    if pattern.match(param):
        return True, ''
    return False, 'illegal charactor found'

def check_username(username):
    return check_param(username, pattern=re_normal, min_len=2, max_len=32)

def check_password(password):
    return check_param(password, pattern=re_all, min_len=6, max_len=32)

def valid_code(code):
    return True

def _login(username='', password=''):
    res, msg = check_username(username)
    if not res:
        return False, '\'username\' ' + msg
    res, msg = check_password(password)
    if not res:
        return False, '\'password\' ' + msg

    users = db.select('user', limitation={'username': username})
    if len(users) == 0:
        return False, 'Invalid username!'

    user = users[0]
    if encrypt(password) != user['password']:
        return False, 'Wrong password!'

    cur_time = get_cur_time()
    cur_ip = request.remote_addr

    login_history = pickle.loads(user.get('history'))
    login_history.append({
        'time': cur_time,
        'ip': cur_ip,
    })

    login_history = pickle.dumps(login_history[-10:])
    user['history'] = login_history

    db.upd_row('user', limitation={'id': user['id']}, \
            data=user)

    session['login'] = {
        'username': username,
        'nickname': user.get('nickname', ''),
        'login_time': time.time(),
        'ip': cur_ip,
    }
    return True, 'login successfully'
    
def _register(username='', password='', nickname='', code='', login=False):
    if nickname == '':
        nickname = username
    res, msg = check_username(username)
    if not res:
        return False, '\'username\' ' + msg
    res, msg = check_password(password)
    if not res:
        return False, '\'password\' ' + msg
    res, msg = check_param(nickname, pattern=re_all, min_len=1)
    if not res:
        return False, '\'nickname\' ' + msg
    res, msg = check_param(code, pattern=re_all, min_len=0)
    if not res:
        return False, '\'code\' ' + msg
    if not valid_code(code):
        return False, 'not valid code'

    if db.count('user', limitation={'username': username}) > 0:
        return False, 'username \'{}\' already exists'.format(username)

    try:
        res = db.add_row('user', data={
            'username': username,
            'password': password,
            'code': code,
            'nickname': nickname,
            'level': 0,
            'history': pickle.dumps([]),
        })
    except:
        return False, 'username \'{}\' already exists'.format(username)
    if login == 'false':
        return True, 'register successfully' 
    status, msg = _login(username, password)
    return status, 'register successfully. ' + msg



@app.route('/logout', methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        data = request.form.to_dict()
        status, msg = _login(**data)
        return jsonify({'ok': status, 'msg': msg})
    return html('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        data = request.form.to_dict()
        status, msg = _register(**data)
        return jsonify({'ok': status, 'msg': msg})
    return html('register.html')

