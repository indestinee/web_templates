from web import *

@app.route('/')
def index():
    return 'hi'

@app.route('/test')
def test():
    return html('test.html')
