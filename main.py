from flask import Flask, render_template, redirect, url_for, request, flash, request, jsonify, abort
from flask_restful import Resource, Api, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from flask_wtf import FlaskForm
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, News
from werkzeug.security import generate_password_hash, check_password_hash
from login_form import LoginForm, RegisterForm
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'

api = Api(app)

app.json.ensure_ascii = False

# Настройка Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Подключаемся и создаем сессию базы данных
engine = create_engine('sqlite:///news.db?check_same_thread=False', echo=True)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Обертка для интеграции SQLAlchemy модели в Flask-Login
class UserLogin(UserMixin):
    def __init__(self, user):
        self.id = str(user.id)
        self.user = user

    @staticmethod
    def get(user_id):
        user = session.query(User).filter_by(id=int(user_id)).first()
        if user:
            return UserLogin(user)
        return None

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False



@login_manager.user_loader
def load_user(user_id):
    user_obj = session.query(User).filter_by(id=int(user_id)).first()
    if user_obj:
        return UserLogin(user_obj)
    return None

# Вспомогательные функции
def abort_if_user_doesnt_exist(user_id):
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        abort(404, message=f"User {user_id} doesn't exist")

def abort_if_news_doesnt_exist(news_id):
    news = session.query(News).filter_by(id=news_id).first()
    if not news:
        abort(404, message=f"News {news_id} doesn't exist")


# Ресурс для пользователей
class UserResource(Resource):
    def get(self, user_id=None):
        if user_id:
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                abort(404, message="User not found")
                return jsonify({
                    'id': user.id,
                    'name': user.name,
                    'about': user.about,
                    'email': user.email,
                    'created_date': user.created_date.isoformat()
                })
        else:
            users = session.query(User).all()
            return jsonify([{
                'id': u.id,
                'name': u.name,
                'about': u.about,
                'email': u.email,
                'created_date': u.created_date.isoformat()
            } for u in users])

    def post(self):
        data = request.get_json()
        new_user = User(
            name=data.get('name'),
            email=data.get('email'),
            hashed_password=generate_password_hash(data.get('password'))
        )
        session.add(new_user)
        session.commit()
        return jsonify({'message': 'User created', 'id': new_user.id})

    def put(self, user_id):
        abort_if_user_doesnt_exist(user_id)
        user = session.query(User).filter_by(id=user_id).first()
        data = request.get_json()
        user.name = data.get('name', user.name)
        user.about = data.get('about', user.about)
        session.commit()
        return jsonify({'message': 'User updated'})

    def delete(self, user_id):
        abort_if_user_doesnt_exist(user_id)
        user = session.query(User).filter_by(id=user_id).first()
        session.delete(user)
        session.commit()
        return jsonify({'message': 'User deleted'})


# Ресурс для новостей
class NewsResource(Resource):
    def get(self, news_id=None):
        if news_id:
            news_item = session.query(News).filter_by(id=news_id).first()
            if not news_item:
                abort(404, message="News not found")
            return jsonify({
                'id': news_item.id,
                'header': news_item.header,
                'text': news_item.text,
                'user_id': news_item.user_id
            })
        else:
            news_list = session.query(News).all()
            return jsonify([{
                'id': n.id,
                'header': n.header,
                'text': n.text,
                'user_id': n.user_id
            } for n in news_list])

    def post(self):
        data = request.get_json()
        new_news = News(
            header=data.get('header'),
            text=data.get('text'),
            user_id=data.get('user_id')
        )
        session.add(new_news)
        session.commit()
        return jsonify({'message': 'News created', 'id': new_news.id})

    def put(self, news_id):
        abort_if_news_doesnt_exist(news_id)
        news_item = session.query(News).filter_by(id=news_id).first()
        data = request.get_json()
        news_item.header = data.get('header', news_item.header)
        news_item.text = data.get('text', news_item.text)
        if 'user_id' in data:
            news_item.user_id = data['user_id']
        session.commit()
        return jsonify({'message': 'News updated'})

    def delete(self, news_id):
        abort_if_news_doesnt_exist(news_id)
        news_item = session.query(News).filter_by(id=news_id).first()
        session.delete(news_item)
        session.commit()
        return jsonify({'message': 'News deleted'})

# Регистрация маршрутов
api.add_resource(UserResource, '/api/users', '/api/users/<int:user_id>')
api.add_resource(NewsResource, '/api/news', '/api/news/<int:news_id>')



@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = session.query(User).filter_by(email=form.email.data).first()
        if user and check_password_hash(user.hashed_password, form.password.data):
            user_obj = UserLogin(user)
            login_user(user_obj)
            flash('Вы успешно вошли в аккаунт', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверные данные для входа', 'danger')
    return render_template('login.html', form=form, title="Авторизация", active_page='login')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из аккаунта', 'success')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if session.query(User).filter_by(email=form.email.data).first():
            flash('Пользователь с этой почтой уже зарегистрирован', 'danger')
        else:
            new_user = User(
                name=form.name.data,
                email=form.email.data,
                hashed_password=generate_password_hash(form.password.data)
            )
            session.add(new_user)
            session.commit()
            flash('Регистрация прошла успешно', 'success')
            return redirect(url_for('login'))
    return render_template('register.html', form=form, title="Регистрация", active_page='register')


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        new_name = request.form.get('name')
        new_about = request.form.get('about')
        new_password = request.form.get('password')

        user = session.query(User).filter_by(id=int(current_user.id)).first()

        if new_name:
            user.name = new_name
        if new_about:
            user.about = new_about
        if new_password:
            user.hashed_password = generate_password_hash(new_password)

        session.commit()
        flash('Профиль успешно обновлен', 'success')
        return redirect(url_for('index'))
    return render_template('edit_profile.html')


@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    user = session.query(User).filter_by(id=int(current_user.id)).first()
    session.query(News).filter_by(user_id=user.id).delete() # удаляем все новости пользователя

    # Удаляем пользователя
    session.delete(user)
    session.commit()
    logout_user()

    flash('Ваш аккаунт был удален', 'info')
    return redirect(url_for('index'))


@app.errorhandler(404)
def error():
    return jsonify({"error": 404}), 404

# страница, которая будет отображать все новости в базе данных
# Эта функция работает в режиме чтения.
@app.route('/')
@app.route('/index')
def index():
    news = session.query(News).all()
    return render_template("index.html", news=news, title="Новости", active_page='index')

@app.route('/my_news')
@login_required
def my_news():
    user_news = session.query(News).filter_by(user_id=current_user.id).all()
    return render_template('index.html', news=user_news, title="Мои новости", active_page='my_news')

# Эта функция позволит создать новость и сохранить ее в базе данных.
@app.route('/news/new/', methods=['GET', 'POST'])
@login_required
def addNews():
    if request.method == 'POST':
        newNews = News(header=request.form['header'],
                       text=request.form['text'],
                       author=current_user.user)
        session.add(newNews)
        session.commit()
        return redirect(url_for('index'))
    else:
        return render_template('newNews.html')


# Эта функция позволит нам обновить книги и сохранить их в базе данных.
@app.route("/news/<int:news_id>/edit/", methods=['GET', 'POST'])
@login_required
def editNews(news_id):
    editedNews = session.query(News).filter_by(id=news_id).one()
    if request.method == 'POST':
        if request.form['header']:
            editedNews.header = request.form['header']
        if request.form['text']:
            editedNews.text = request.form['text']
        session.add(editedNews)
        session.commit()
        return redirect(url_for('index'))
    else:
        return render_template('editNews.html', news=editedNews)

# Эта функция для удаления книг
@app.route('/news/<int:news_id>/delete/', methods=['GET', 'POST'])
@login_required
def deleteNews(news_id):
    newsToDelete = session.query(News).filter_by(id=news_id).one()
    if request.method == 'POST':
        session.delete(newsToDelete)
        session.commit()
        return redirect(url_for('index', news_id=news_id))
    else:
        return render_template('deleteNews.html', news=newsToDelete)

if __name__ =='__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)

#app.run(debug=True)