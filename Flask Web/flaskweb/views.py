# 视图函数（路由）
from flask import render_template, request, url_for, redirect, flash
from flask_login import login_user, login_required, logout_user

from flaskweb import app, db
from flaskweb.models import User

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