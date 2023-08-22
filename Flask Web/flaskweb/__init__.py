# coding=utf-8
import os
import sys
import openai

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy  # 导入扩展类
from flask_login import LoginManager, current_user

WIN = sys.platform.startswith('win')
if WIN:  # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else:  # 否则使用四个斜线
    prefix = 'sqlite:////'

# TODO: 后期改为从文件或系统的环境变量中使用API密钥
openai.api_key="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"

# TODO: 后期部署的数据库存储方式也要修改
app = Flask(__name__)
# 读取系统环境变量DATABASE_FILE,否则使用data.db来作为存储信息的数据库文件名
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(os.path.dirname(app.root_path), os.getenv('DATABASE_FILE', 'data.db'))
# 这个密钥的值在开发时可以随便设置。基于安全的考虑，在部署时应该设置为随机字符，且不应该明文写在代码里
# 读取系统环境变量 SECRET_KEY 的值，如果没有获取到，则使用 dev
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
# 关闭对模型修改的监控
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 在扩展类实例化前加载配置
db = SQLAlchemy(app)  # 初始化扩展，传入程序实例 app
# 导入Bootstrap类，并初始化
bootstrap = Bootstrap(app)

login_manager = LoginManager(app)  # 实例化扩展类
login_manager.login_view = 'login'
# 登录函数
@login_manager.user_loader
def load_user(user_id):  # 创建用户加载回调函数，接受用户 ID 作为参数
    user = User.query.get(int(user_id))  # 用 ID 作为 User 模型的主键查询对应的用户
    return user  # 返回用户对象

# 模板上下文处理函数
@app.context_processor
def inject_user():  # 函数名可以随意修改
    return dict(user=current_user)

from flaskweb import views, errors, commands