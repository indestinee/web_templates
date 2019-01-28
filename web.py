from flask import Flask, render_template, redirect,\
        url_for, request, session,\
        send_from_directory, make_response, jsonify
from web_config import web_cfg
from utils import *
from config import db

app = Flask(__name__, static_folder=web_cfg._static_folder,\
        static_url_path=web_cfg._static_url_path)
app.config['SECRET_KEY'] = web_cfg._secret_key


global_logout_time = {}
def is_login():
    if 'login' not in session:
        return False

    logout_time = global_logout_time.get(session['login']['username'], 0)
    login_time = session['login']['login_time']
    if login_time <= logout_time:
        session.clear()
        return False
    return True

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/logout_all')
def logout_all():
    if 'login' in session:
        global_logout_time[session['login']['username']] = time.time()
    session.clear()
    return redirect(url_for('login'))


allow_path = ['/login', '/register', '/favicon.ico', '/test']
allow_prefix = ['/static/js', '/static/css']

@app.before_request
def check_user():
    if is_login():
        if request.path in {'/login', '/register'}:
            return redirect(url_for('index'))
    else:
        if request.path in allow_path:
            return
        for prefix in allow_prefix:
            if request.path.startswith(prefix):
                return
        return redirect(url_for('login'))


def html(html_name='index.html', **kwargs):
    return render_template(
        html_name,
        enumerate=enumerate,
        len=len, max=max, min=min, zip=zip,
        **kwargs
    )
