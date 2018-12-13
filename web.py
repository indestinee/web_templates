from flask import Flask, render_template, redirect,\
        url_for, request, session,\
        send_from_directory, make_response
from web_config import web_cfg
from utils import *
from config import db

app = Flask(__name__, static_folder=web_cfg._static_folder,\
        static_url_path=web_cfg._static_url_path)
app.config['SECRET_KEY'] = web_cfg._secret_key


global_logout_time = {}
def is_login():
    if 'user' not in session:
        return False
    login_time = session['user']['login_time']
    logout_time = global_logout_time.get(session['user']['username'], None)
    return logout_time is None or logout_time < login_time

@app.before_request
def check_user():
    if is_login():
        return
    if request.path == '/login' or request.path.startswith('/static/'):
        return
    return redirect(url_for('login'))




def html(html_name='index.html', **kwargs):
    return render_template(
        html_name,
        enumerate=enumerate,
        len=len, max=max, min=min, zip=zip,
        **kwargs
    )
