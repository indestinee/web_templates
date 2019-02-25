from web import *

@app.route('/')
@app.route('/index')
@app.route('/home')
def index():
    return html('index.html', active="home")

@app.route('/dashboard')
def dashboard():
    return html('dashboard.html', active="dashboard")

@app.route('/ps')
def ps():
    return jsonify({'ok': True, 'msg': 'succeed', 'data': get_ps(), 'time': time.time()})

if __name__ == "__main__":
    print(ps(jsonfy=False))
