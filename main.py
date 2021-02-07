import datetime
import json
from flask import Flask, render_template, request, url_for, redirect, flash
from flask_bootstrap import Bootstrap
from forms import UpdateSavedUser, RegisterUserForm, SearchUserForm, LoginUserForm
from github_api_operations import fetch_repositories, fetch_users, fetch_user, fetch_user_languages
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from os import getenv, path

app = Flask(__name__)
app.config['SECRET_KEY'] = getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


login_manager = LoginManager()
login_manager.init_app(app)
db = SQLAlchemy(app)
Bootstrap(app)


# User class for registered users
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))


# Class for saved github profiles
class SavedProfiles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String)
    html_url = db.Column(db.String, unique=True)
    avatar_url = db.Column(db.String)
    name = db.Column(db.String)
    hireable = db.Column(db.Boolean)
    twitter_username = db.Column(db.String)
    location = db.Column(db.String)
    email = db.Column(db.String)
    company = db.Column(db.String)
    languages = db.Column(db.String)
    total_language = db.Column(db.Integer)
    repositories = db.Column(db.String)


# if the database does not exist yet, it is created
if not path.exists('./users.db'):
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login')


@app.route("/")
def home():
    return render_template("index.html", logged_in=current_user.is_authenticated)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterUserForm()
    if form.validate_on_submit():
        new_user = User(
            email=request.form['email'],
            password=generate_password_hash(request.form['password'], method='pbkdf2:sha256', salt_length=8),
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('search'))
    return render_template('register.html', form=form, logged_in=current_user.is_authenticated)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginUserForm()
    if form.validate_on_submit():
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash("Password incorrect, please try again.")
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('search'))
    return render_template('login.html', form=form, logged_in=current_user.is_authenticated)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/search", methods=["GET", "POST"])
def search():
    form = SearchUserForm()
    if request.method == "POST":
        username = request.form.get('username')
        users = fetch_users(username)
        return render_template("search.html", users=users, form=form, logged_in=current_user.is_authenticated)
    return render_template("search.html", form=form, logged_in=current_user.is_authenticated)


@app.route("/details/<username>")
def details(username):
    user = fetch_user(username)
    repositories = fetch_repositories(username)
    saved = False
    languages = fetch_user_languages(user, repositories)
    total_language = sum(languages.values())
    saved_user = SavedProfiles.query.filter_by(html_url=user['html_url']).first()
    if saved_user:
        saved = True
    return render_template('details.html', user=user, repos=repositories, languages=languages,
                           total=total_language, logged_in=current_user.is_authenticated, saved=saved)


@app.route("/saved_users", methods=["GET", "POST"])
@login_required
def saved_users():
    users = SavedProfiles.query.all()
    if users:
        for user in users:
            user.languages = json.loads(user.languages)
            user.repositories = json.loads(user.repositories)
    return render_template('saved_users.html', logged_in=current_user.is_authenticated, users=users)


@app.route("/save_user/<username>", methods=["GET"])
@login_required
def save_user(username):
    user = fetch_user(username)
    user_repositories = fetch_repositories(user['login'])
    repositories = json.dumps(user_repositories)
    user_languages = fetch_user_languages(username=user, repositories=user_repositories)
    languages = json.dumps(user_languages)
    total_language = sum(user_languages.values())
    if not SavedProfiles.query.filter_by(html_url=user['html_url']).first():
        new_user = SavedProfiles(
            login=user['login'],
            html_url=user['html_url'],
            avatar_url=user['avatar_url'],
            name=user['name'],
            hireable=user['hireable'],
            twitter_username=user['twitter_username'],
            location=user['location'],
            email=user['email'],
            company=user['company'],
            repositories=repositories,
            languages=languages,
            total_language=total_language,
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('saved_users', logged_in=current_user.is_authenticated))


@app.route("/update_saved_user/<user_id>", methods=["GET", "POST"])
@login_required
def update_saved_user(user_id):
    user = SavedProfiles.query.get(user_id)
    form = UpdateSavedUser(
        name=user.name,
        twitter_username=user.twitter_username,
        location=user.location,
        email=user.email,
        company=user.company,
    )
    if form.validate_on_submit():
        user.name = form.name.data
        user.twitter_username = form.twitter_username.data
        user.location = form.location.data
        user.email = form.email.data
        user.company = form.company.data
        db.session.commit()
        return redirect(url_for('saved_users'))
    return render_template('update_saved_user.html', form=form)


@app.route("/delete_user/<int:user_id>")
@login_required
def delete_user(user_id):
    user = SavedProfiles.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('saved_users'))


"""
A function that will keep the current year in the footer up to date
"""


@app.context_processor
def current_year():
    now = datetime.datetime.now()
    return {'year': now.year}


if __name__ == "__main__":
    app.run(debug=True)
