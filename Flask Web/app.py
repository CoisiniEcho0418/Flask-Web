# coding=utf-8
import os
import sys
import click
import openai

from flask import Flask, render_template,request, url_for, redirect, flash
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy  # 导入扩展类
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager,UserMixin,login_user,login_required, logout_user,current_user


WIN = sys.platform.startswith('win')
if WIN:  # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else:  # 否则使用四个斜线
    prefix = 'sqlite:////'

# TODO: 后期改为从文件或系统的环境变量中使用API密钥
openai.api_key="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"

# TODO: 后期部署的数据库存储方式也要修改
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db') # data.db是用来存储信息的数据库表
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控
# 这个密钥的值在开发时可以随便设置。基于安全的考虑，在部署时应该设置为随机字符，且不应该明文写在代码里
app.config['SECRET_KEY'] = 'dev'  # 等同于 app.secret_key = 'dev'
# 在扩展类实例化前加载配置
db = SQLAlchemy(app)  # 初始化扩展，传入程序实例 app
# 导入Bootstrap类，并初始化
bootstrap = Bootstrap(app)

# 类设计
# 用户类
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))  # 用户名
    password_hash = db.Column(db.String(128))  # 密码散列值

    def set_password(self, password):  # 用来设置密码的方法，接受密码作为参数
        self.password_hash = generate_password_hash(password)  # 将生成的密码保持到对应字段

    def validate_password(self, password):  # 用于验证密码的方法，接受密码作为参数
        return check_password_hash(self.password_hash, password)  # 返回布尔值


# 命令行执行的initdb函数
@app.cli.command()  # 注册为命令，可以传入 name 参数来自定义命令
@click.option('--drop', is_flag=True, help='Create after drop.')  # 设置选项
def initdb(drop):
    """Initialize the database."""
    if drop:  # 判断是否输入了选项
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')  # 输出提示信息


# 模板上下文处理函数
@app.context_processor
def inject_user():  # 函数名可以随意修改
    return dict(user=current_user)

# 404处理函数
@app.errorhandler(404)  # 传入要处理的错误代码
def page_not_found(e):  # 接受异常对象作为参数
    return render_template('404.html'), 404  # 返回模板和状态码

login_manager = LoginManager(app)  # 实例化扩展类
login_manager.login_view = 'login'
# 登录函数
@login_manager.user_loader
def load_user(user_id):  # 创建用户加载回调函数，接受用户 ID 作为参数
    user = User.query.get(int(user_id))  # 用 ID 作为 User 模型的主键查询对应的用户
    return user  # 返回用户对象

# 用户登录模块
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))

        # 查询用户名对应的用户记录
        user = User.query.filter_by(username=username).first()
        # 验证用户名和密码是否一致
        if username == user.username and user.validate_password(password):
            login_user(user)  # 登入用户
            flash('Login success.')
            return redirect(url_for('index'))  # 重定向到主页

        flash('Invalid username or password.')  # 如果验证失败，显示错误消息
        return redirect(url_for('login'))  # 重定向回登录页面

    return render_template('login.html')

# 用户注册模块
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Please provide both username and password.', 'danger')
            return redirect(url_for('register'))

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different username.', 'danger')
            return redirect(url_for('register'))

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# 登出模块
@app.route('/logout')
@login_required  # 用于视图保护
def logout():
    logout_user()  # 登出用户
    flash('Goodbye.')
    return redirect(url_for('index'))  # 重定向回首页

# 修改密码模块
@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']

        # Validate if the current password matches the user's password
        if not current_user.validate_password(current_password):
            flash('Current password is incorrect.')
            return redirect(url_for('settings'))

        if current_password == new_password:
            flash('New password should be different from the current password.')
            return redirect(url_for('settings'))

        # Update the user's password and commit changes
        current_user.set_password(new_password)
        db.session.commit()

        flash('Password updated successfully.')
        return redirect(url_for('index'))

    return render_template('settings.html')


# 主页视图函数
@app.route('/', methods=['GET', 'POST'])
def index():
    generated_image_urls = []

    if request.method == 'POST':
        prompt = request.form['prompt']
        # 调用 OpenAI 的文本-图像生成接口并获取生成的图片链接
        for _ in range(3):  # 生成三张图片
            response = openai.Image.create(
                prompt=prompt,
                n=1,
                size="1024x1024"
            )
            generated_image_url = response['data'][0]['url']
            generated_image_urls.append(generated_image_url)

        # 返回包含图片链接的渲染模板
        return render_template('index.html', prompt=prompt, generated_image_urls=generated_image_urls)

    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


