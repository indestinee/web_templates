import flask, os

from web_config import web_cfg
from database import db

active_pages = [
    {'name': 'home',},
    {'name': 'ftp', 'ico': 'fa fa-server'},
    {'name': 'dashboard', 'ico': 'fa fa-dashboard'},
]

active_pages_names = {item['name'] for item in active_pages}

app = flask.Flask(__name__, static_folder=web_cfg._static_folder,
            static_url_path=web_cfg._static_url_path)
app.config['SECRET_KEY'] = web_cfg._secret_key

allow_path = ['/login', '/register', '/favicon.ico']
allow_prefix = ['/static/',]


def is_login():
    return 'login' in flask.session


@app.route('/favicon.ico')
def favicon():
    return flask.send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico', mimetype='image/vnd.microsoft.icon'
    )


@app.before_request
def check_user():
    return
    if is_login():
        if flask.request.path in {'/login', '/register'}:
            return flask.redirect(flask.url_for('index'))
    else:
        if flask.request.path in allow_path:
            return
        for prefix in allow_prefix:
            if flask.request.path.startswith(prefix):
                return
        return flask.redirect(flask.url_for('web_login'))


def html(html_name='index.html', **kwargs):
    return flask.render_template(
        html_name,
        active_pages=active_pages,
        enumerate=enumerate,
        len=len, max=max, min=min, zip=zip,
        **kwargs
    )
