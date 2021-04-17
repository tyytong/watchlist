from flask import Flask
from flask import url_for
app = Flask(__name__)


@app.route('/')
def hello():
    return '<h1>Hello Totoro!</h1><img src="http://helloflask.com/totoro.gif">'


@app.route('/user/<name>')
def user_page(name):
    return 'User: {}'.format(name)


@app.route('/test')
def test_url_for():
    print(url_for('hello'))
    print(url_for('user_page', name='ttt'))
    print(url_for('user_page', name='yyy'))
    print(url_for('test_url_for'))
    # 这里调用传入了多余的关键字参数，他们会作为查询字符串附加到 URL 后面
    print(url_for('test_url_for', num=2))
    return 'Test Page'