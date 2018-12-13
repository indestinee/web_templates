from web import *


def encrypt(data):
    return data

def valid_user(username, password):
    users = db.select('user', limitation={'username': username})
    if len(users) == 0 or encrypt(password) != users[0]['password']:
        return None
    user = users[0]
    _time = cur_time()
    user['login_time'] = _time
    db.upd_row('user', limitation={'username': username}, data={'last_login': _time})

    return user

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        user = valid_user(username, password)
        if user is not None:
            session['user'] = user
            return redirect(url_for('index'))
        
    return html('login.html')
