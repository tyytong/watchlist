import os
import sys
import click

from flask import Flask, render_template
from flask import url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy

prefix = 'sqlite:////'
app = Flask(__name__)
print('path:', prefix + os.path.join(app.root_path, 'data.db'))
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控
# flash需要设置签名所需的秘钥
app.config['SECRET_KEY'] = 'dev'

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


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # 获取表单数据
        title = request.form.get('title')   # 传入表单对应输入字段的 name 值
        year = request.form.get('year')
        # 验证数据
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input.')   # 显示错误提示
            return redirect(url_for('index'))  # 重定向回主页
        # 保存表单数据到数据库
        movie = Movie(title=title, year=year)   # 创建记录
        db.session.add(movie)  # 添加到数据库会话
        db.session.commit()
        flash('Item created.')
        return redirect(url_for('index'))

    movies = Movie.query.all()
    return render_template('index.html', movies=movies)


# 模板上下文处理函数
@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)   # 需要返回字典, 等同于 return {'user': user}


@app.errorhandler(404)   # 传入要处理的错误代码
def page_not_found(e):
    return render_template('404.html'), 404    # 返回模板和状态码


# 编辑电影条目
@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':  # 处理编辑表单的提交请求
        title = request.form['title']
        year = request.form['year']

        if not title or not year or len(year) != 4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('edit', movie_id=movie_id))

        movie.title = title  # 更新标题
        movie.year = year  # 更新年份
        db.session.commit()
        flash('Item update.')
        return redirect(url_for('index'))

    return render_template('edit.html', movie=movie)


# 删除电影条目
@app.route('/movie/delete/<int:movie_id>', methods=['POST'])
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted.')
    return redirect(url_for('index'))
