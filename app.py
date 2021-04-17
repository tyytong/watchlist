import os
import sys
import click

from flask import Flask, render_template
from flask import url_for
from flask_sqlalchemy import SQLAlchemy

prefix = 'sqlite:////'
app = Flask(__name__)
print('path:', prefix + os.path.join(app.root_path, 'data.db'))
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控

db = SQLAlchemy(app)


# 创建数据库模型 表
class User(db.Model):     # 表名将会是 user (自动生成 小写处理)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))


# 定义命令自动执行创建数据库表操作
@app.cli.command()  # 注册为命令
def forge():
    """Generate fake data"""
    db.create_all()
    # 全局变量
    name = 'Test'
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
        {'title': 'The Pork of Music', 'year': '2012'},
    ]

    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m['title'], year=m['year'])
        db.session.add(movie)

    db.session.commit()
    click.echo('Done.')


@click.option('--drop', is_flag=True, help='Create after drop.')   # 设置选项
def initdb(drop):
    """Initialize the database."""
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')


# @app.route('/')
# def hello():
#     return '<h1>Hello Totoro!</h1><img src="http://helloflask.com/totoro.gif">'


@app.route('/user/<name>')
def user_page(name):
    return 'User: {}'.format(name)


@app.route('/test')
def test_url_for():
    # print(url_for('hello'))
    print(url_for('user_page', name='ttt'))
    print(url_for('user_page', name='yyy'))
    print(url_for('test_url_for'))
    # 这里调用传入了多余的关键字参数，他们会作为查询字符串附加到 URL 后面
    print(url_for('test_url_for', num=2))
    return 'Test Page'


@app.route('/')
def index():
    user = User.query.first()
    movies = Movie.query.all()
    return render_template('index.html', user=user, movies=movies)
