import flask, os

from web import app, html, active_pages_names
from tools import check_path, run
import login, ftp, ps, shutil


@app.route('/')
@app.route('/index')
@app.route('/home')
def web_index():
    return html('index.html', active="home")


@app.route('/dashboard')
def web_dashboard():
    if 'dashboard' not in active_pages_names:
        flask.abort(404)
    return html('dashboard.html', active="dashboard")


@app.route('/ps')
def web_ps():
    if 'dashboard' not in active_pages_names:
        flask.abort(404)
    try:
        from_time = float(flask.request.args.get('from_time'))
    except Exception as e:
        from_time = None
    return flask.jsonify({
        'ok': True, 'msg': 'succeed', 'data': ps.get_runtime_rss(from_time)
    })


@app.route('/ftp')
def web_ftp():
    if 'ftp' not in active_pages_names:
        flask.abort(404)
    return html('ftp.html', active='ftp')

@app.route('/edit')
def web_edit():
    if 'ftp' not in active_pages_names:
        flask.abort(404)
    return 'NOT FINISH'


@app.route('/upload', methods=['POST'])
def web_upload():
    if 'ftp' not in active_pages_names:
        flask.abort(404)
    
    path = flask.request.form.get('path', None)
    if path is None:
        return flask.jsonify({'ok': False, 'msg': 'you must specify path'})
    local_path = check_path(path)
    filename = flask.request.form.get('filename', None)
    file1 = flask.request.files.get('file1', None)

    if filename is not None and file1 is not None:
        save_path = check_path(filename, local_path)
        file1.save(save_path)
        return flask.jsonify({'ok': True, 'msg': 'save successfully, path: {}'.format(save_path)})

    url = flask.request.form.get('url', None)
    t = flask.request.form.get('type', None)
    if url is not None and t is not None:
        if t in ['url', 'audio', 'video']:
            filename = url.split('/')[-1]
            if len(filename) == 0:
                filename = 'index.html'
            index = ftp.download(url, local_path, t)
            return flask.jsonify({'ok': True, 'msg': '#{} task is downloading'.format(index)})
    return flask.jsonify({'ok': False, 'msg': 'error, nothing happened'})
    
    



@app.route('/delete', methods=['post'])
def delete():
    if 'ftp' not in active_pages_names:
        flask.abort(404)
    path = flask.request.form.get('path', None)
    if path is None:
        return flask.jsonify({'ok': False, 'msg': 'you must specify path'})

    local_path = check_path(path)
    try:
        if os.path.islink(local_path):
            os.unlink(local_path)
        elif os.path.isfile(local_path):
            os.remove(local_path)
        else:
            msg = shutil.rmtree(local_path)
        return flask.jsonify({'ok': True, 'msg': 'delete successfully'})
    except Exception as e:
        return flask.jsonify({'ok': False, 'msg': '{}'.format(e)})


@app.route('/download')
def download():
    path = flask.request.args.get('path', '.')
    local_path = check_path(path)
    if os.path.isfile(local_path):
        return flask.send_from_directory(
            os.path.dirname(local_path),
            os.path.basename(local_path),
            as_attachment=True
        )
    flask.abort(404)


@app.route('/get_files')
def web_get_files():
    if 'ftp' not in active_pages_names:
        flask.abort(404)
    path = flask.request.args.get('path', '.')
    local_path = check_path(path)
    return flask.jsonify({
        'ok': True, 'msg': 'succeed',
        'data': ftp.get_files(local_path),
        'path': path
    })


logout_msg = '''
<div class="alert alert-success" role="alert">
    Log out! Bye~
    <button type="button" class="close" data-dismiss="alert" aria-label="Close">
        <i class="fa fa-close"></i>
    </button>
</div>
'''


@app.route('/logout', methods=["GET"])
def logout():
    flask.session.clear()
    return flask.redirect(flask.url_for('web_login', logout=1))


@app.route('/login', methods=['POST', 'GET'])
def web_login():
    if flask.request.method == 'POST':
        data = flask.request.form.to_dict()
        status, msg = login.login(**data)
        return flask.jsonify({'ok': status, 'msg': msg})
    msg = logout_msg if flask.request.args.get('logout', '0') == '1' else ''
    return html('login.html', msg=msg)


@app.route('/register', methods=['POST', 'GET'])
def web_register():
    if flask.request.method == 'POST':
        data = flask.request.form.to_dict()
        status, msg = login.register(**data)
        return flask.jsonify({'ok': status, 'msg': msg})
    return flask.redirect('/login#toregister')
