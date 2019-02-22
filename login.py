from web import *
import re, pickle

re_all = re.compile(r'^.*$')
re_normal = re.compile(r'^\w+$')

def valid_code(code):
    return True
    codes = [code['code'] for code in db.select('code', keys='code',\
            limitation='valid>{}'.format(time.time()))]
    return code in codes 

def check_param(param, name, *, pattern=re_normal, min_len=6, max_len=32):
    if len(param) < min_len or len(param) > max_len:
        return False, '{}\'s length should be within [{}, {}].'.format(\
                name, min_len, max_len)
    if pattern.match(param): return True, ''
    return False, 'Illegal charactor found!'


def _login(username='', password=''):
    users = db.select('user', limitation={'username': username})
    if len(users) == 0: return False, 'Invalid username!'
    user, = users
    if password != user['password']: return False, 'Invalid password!'


    session['login'] = {
        'id': user['id'],
        'username': username,
    }
    add_log('{} login from {} at {} {}.'.format(username,\
            request.remote_addr, get_cur_time(), time.tzname[0]), user_id=user['id'])
    return True, 'Login successfully!'
    
def _register(username='', password='', code='', login=False):
    res, msg = check_param(username, 'Username',\
            pattern=re_normal, min_len=2, max_len=32)
    if not res: return False, msg

    res, msg = check_param(password, 'Password',\
            pattern=re_all, min_len=6, max_len=32)
    if not res: return False, msg

    if not valid_code(code): return False, 'Invalid invitation code.'

    try:
        res = db.add_row('user', data={
            'username': username,
            'password': password,
            'code': code,
            'level': 0,
        })
        user, = db.select('user', limitation={'username': username})
        add_log('{} register from {} at {} {}.'.format(username,\
                request.remote_addr, get_cur_time(), time.tzname[0]), user_id=user['id'])
    except Exception as e:
        raise(e)

    status, msg = True, 'Register successfully!' 
    if login == 'true': status, msg = _login(username, password)
    return status, msg

logout_msg = '''
<div class="alert alert-success" role="alert">Log out! Bye~
    <button type="button" class="close" data-dismiss="alert" aria-label="Close">
        <span aria-hidden="true">×</span>
    </button>
</div>
'''


@app.route('/logout', methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for('login', logout=1))

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        data = request.form.to_dict()
        status, msg = _login(**data)
        return jsonify({'ok': status, 'msg': msg})
    print(request.args.get('logout'))
    msg = logout_msg if request.args.get('logout', '0') == '1' else ''
    return html('login.html', msg=msg)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        data = request.form.to_dict()
        status, msg = _register(**data)
        return jsonify({'ok': status, 'msg': msg})
    return html('register.html')

