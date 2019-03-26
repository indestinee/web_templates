from flask import Flask, render_template, redirect,\
        url_for, request, session,\
        send_from_directory, make_response, jsonify
from web_config import web_cfg
from eic_utils import *
from config import db
from tools import *

app = Flask(__name__, static_folder=web_cfg._static_folder,\
        static_url_path=web_cfg._static_url_path)
app.config['SECRET_KEY'] = web_cfg._secret_key

allow_path = ['/login', '/register', '/favicon.ico', '/test']
allow_prefix = ['/static/',]

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),\
            'favicon.ico', mimetype='image/vnd.microsoft.icon')

def is_login():
    return 'login' in session

@app.before_request
def check_user():
    return
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
