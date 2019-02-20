from web import *

@app.route('/')
def index():
    return html(
        'index.html',
    )

@app.route('/test')
def test():
    return html('test.html')
